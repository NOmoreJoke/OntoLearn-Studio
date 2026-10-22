"""Text-only Turtle parsing with local, lossless RDF literal construction.

The pinned RDFLib productions parse the text. Literal construction preserves
spelling and a Turtle statement guard rejects silently discarded orphan terms;
no process-wide normalization or parser settings are changed.
"""

import re
from dataclasses import dataclass
from decimal import Decimal
from hashlib import sha256
from ipaddress import IPv6Address
from types import MappingProxyType
from weakref import ref

from rdflib import OWL, RDF, RDFS, SH, XSD, BNode, Graph, Literal, URIRef
from rdflib.plugins.parsers.notation3 import RDFSink, SinkParser, sfloat


def canonical_string(term):
    """Use S1's plain representation for one RDF 1.1 string term identity.

    Numeric/date spelling and language-tagged literals are deliberately untouched.
    This is local to our semantic view, never a process-wide RDFLib setting.
    """
    if isinstance(term, Literal) and term.datatype == XSD.string and term.language is None:
        return Literal(str(term), normalize=False)
    return term


class LexicalSink(RDFSink):
    def __init__(self, graph, *, canonical_strings=True):
        super().__init__(graph)
        self.canonical_strings = canonical_strings

    def newLiteral(self, text, datatype, language):
        term = Literal(text, datatype=datatype, lang=language, normalize=False)
        return canonical_string(term) if self.canonical_strings else term


class LexicalSinkParser(SinkParser):
    def __init__(self, *args, **kwargs):
        self._emitted_statements = 0
        super().__init__(*args, **kwargs)

    def makeStatement(self, quadruple):
        self._emitted_statements += 1
        return super().makeStatement(quadruple)

    def statement(self, argstr, i):
        # RDFLib also accepts an empty property list after any standalone term,
        # silently dropping it (e.g. the orphan .3 in "1.2.3 ."). Turtle triples
        # require predicates unless the subject is a blankNodePropertyList.
        # Count emission events, not graph size: duplicate triples are valid.
        start, before_subject = i, self._emitted_statements
        subject = []
        i = self.object(argstr, i, subject)
        if i < 0:
            return i
        after_subject = self._emitted_statements
        end = self.property_list(argstr, i, subject[0])
        if end < 0:
            self.BadSyntax(argstr, i, "expected propertylist")
        if self._emitted_statements == after_subject and not (
            argstr[start : start + 1] == "[" and after_subject > before_subject
        ):
            self.BadSyntax(argstr, i, "expected nonempty Turtle propertylist")
        return end

    def nodeOrLiteral(self, argstr, i, res):
        count = len(res)
        end = super().nodeOrLiteral(argstr, i, res)
        for index in range(count, len(res)) if end >= 0 else ():
            # Exact types exclude bool. Scientific notation is RDFLib's sfloat
            # (a str subclass), not float. Recover spelling before the sink
            # converts the parser's Python numeric values into RDF literals.
            datatype = {int: XSD.integer, Decimal: XSD.decimal, sfloat: XSD.double}.get(
                type(res[index])
            )
            if datatype is not None:
                lines, start_of_line = self.lines, self.startOfLine
                try:
                    start = self.skipSpace(argstr, i)
                finally:
                    # skipSpace changes location state; preserve the original
                    # parse's error positions and generated blank-node identity.
                    self.lines, self.startOfLine = lines, start_of_line
                res[index] = Literal(argstr[start:end], datatype=datatype, normalize=False)
        return end


def parse_graph(text, *, base_uri):
    """Caller owns text limits, offline context, term and triple validation."""
    graph = Graph()
    parser = LexicalSinkParser(LexicalSink(graph), baseURI=base_uri, turtle=True)
    parser.loadBuf(text)
    for prefix, namespace in parser._bindings.items():
        graph.bind(prefix, namespace)
    return graph


# Profile entry points are deliberately separate: legacy parsing above retains
# its exact policy. No RDFLib conversion table, parser or logger is patched here.
_PROFILE_TEXT_BYTES = 1_048_576
_PROFILE_TRIPLES = 100_000
_PROFILE_OCCURRENCES = 300_000
_SCHEME = re.compile(r"[A-Za-z][A-Za-z0-9+.-]*:", re.ASCII)
_HEX = frozenset("0123456789abcdefABCDEF")
_UNRESERVED = frozenset("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-._~")
_SUBDELIMS = frozenset("!$&'()*+,;=")
_CONTEXTS = {}
_UNSET = object()


def _profile_fail(code):
    from ontolearn_engine.semantic_offline import SemanticError

    raise SemanticError(code)


def _utf8_bound(text, limit=_PROFILE_TEXT_BYTES):
    if type(text) is not str:
        _profile_fail("TEXT_TYPE_INVALID")
    # Bound before allocating the UTF-8 representation.
    if len(text) > limit:
        _profile_fail("TEXT_INPUT_LIMIT")
    try:
        raw = text.encode("utf-8")
    except UnicodeEncodeError:
        _profile_fail("INVALID_UNICODE")
    if len(raw) > limit:
        _profile_fail("TEXT_INPUT_LIMIT")
    return raw


def _ucschar(cp):
    return (
        0xA0 <= cp <= 0xD7FF
        or 0xF900 <= cp <= 0xFDCF
        or 0xFDF0 <= cp <= 0xFFEF
        or 0x10000 <= cp <= 0xDFFFD
        and cp & 0xFFFF <= 0xFFFD
        or 0xE1000 <= cp <= 0xEFFFD
        and cp & 0xFFFF <= 0xFFFD
    )


def _iri_chars(text, extra="", *, private=False, unicode=True, percent=True):
    at = 0
    while at < len(text):
        char = text[at]
        if char == "%" and percent:
            if at + 2 >= len(text) or any(c not in _HEX for c in text[at + 1 : at + 3]):
                _profile_fail("ABSOLUTE_IRI_REQUIRED")
            at += 3
            continue
        cp = ord(char)
        if not (
            char in _UNRESERVED
            or char in _SUBDELIMS
            or char in extra
            or unicode
            and _ucschar(cp)
            or private
            and (0xE000 <= cp <= 0xF8FF or 0xF0000 <= cp <= 0x10FFFD and cp & 0xFFFF <= 0xFFFD)
        ):
            _profile_fail("ABSOLUTE_IRI_REQUIRED")
        at += 1


def _iri_authority(authority):
    if authority.count("@") > 1:
        _profile_fail("ABSOLUTE_IRI_REQUIRED")
    if "@" in authority:
        user, authority = authority.split("@", 1)
        _iri_chars(user, ":")
    if authority.startswith("["):
        close = authority.find("]")
        if close < 0:
            _profile_fail("ABSOLUTE_IRI_REQUIRED")
        address, tail = authority[1:close], authority[close + 1 :]
        if tail and not tail.startswith(":"):
            _profile_fail("ABSOLUTE_IRI_REQUIRED")
        port = tail[1:] if tail else ""
        if address[:1].lower() == "v":
            version, dot, future = address[1:].partition(".")
            if not dot or not version or any(c not in _HEX for c in version) or not future:
                _profile_fail("ABSOLUTE_IRI_REQUIRED")
            _iri_chars(future, ":", unicode=False, percent=False)
        else:
            # RFC3987 does not permit zone IDs; IPv6Address itself permits them.
            if "%" in address or len(address) > 45:
                _profile_fail("ABSOLUTE_IRI_REQUIRED")
            try:
                IPv6Address(address)
            except ValueError:
                _profile_fail("ABSOLUTE_IRI_REQUIRED")
    else:
        if authority.count(":") > 1:
            _profile_fail("ABSOLUTE_IRI_REQUIRED")
        host, separator, port = authority.partition(":")
        _iri_chars(host)
        if not separator:
            port = ""
    if any(c not in "0123456789" for c in port):
        _profile_fail("ABSOLUTE_IRI_REQUIRED")


def validate_profile_iri(text):
    """RFC3987 IRI (scheme required, fragment allowed), without normalization/I/O.

    RDF1.1 section 3.2 uses this production, not the fragment-free absolute-IRI.
    This validates generic syntax; it does not assert scheme-specific semantics,
    host existence, an IANA registration, IDNA equivalence or access permission.
    """
    _utf8_bound(text, 16384)
    scheme = _SCHEME.match(text)
    if scheme is None:
        _profile_fail("ABSOLUTE_IRI_REQUIRED")
    hierarchy, fragment_marker, fragment = text[scheme.end() :].partition("#")
    hierarchy, query_marker, query = hierarchy.partition("?")
    if fragment_marker:
        _iri_chars(fragment, ":@/?")
    if query_marker:
        _iri_chars(query, ":@/?", private=True)
    if hierarchy.startswith("//"):
        authority, slash, path = hierarchy[2:].partition("/")
        _iri_authority(authority)
        if slash:
            _iri_chars(path, ":@/")
    else:
        _iri_chars(hierarchy, ":@/")
    return text


def _term_input(term, source=None, *, datatype=_UNSET, language=_UNSET, lexical=None):
    from ontolearn_engine.quality.rule_profile import TermInput

    if isinstance(term, URIRef):
        return TermInput("iri", validate_profile_iri(str(term)), source=source)
    if not isinstance(term, Literal):
        _profile_fail("UNSUPPORTED_BLANK_NODE")
    actual_datatype = term.datatype if datatype is _UNSET else datatype
    actual_language = term.language if language is _UNSET else language
    lexical = str(term) if lexical is None else lexical
    _utf8_bound(lexical, 16384)
    if actual_datatype is not None:
        validate_profile_iri(str(actual_datatype))
    return TermInput(
        "literal",
        lexical,
        str(actual_datatype) if actual_datatype is not None else None,
        actual_language,
        source,
    )


def _profile_vocabulary(triple):
    s, p, o = triple
    if not isinstance(s, URIRef | BNode) or not isinstance(p, URIRef):
        _profile_fail("RDF_TERM_INVALID")
    if p == OWL.imports:
        _profile_fail("EXTERNAL_ACCESS_DENIED")
    for term in triple:
        if isinstance(term, URIRef):
            validate_profile_iri(str(term))
            if str(term).startswith(str(OWL)) and term not in {
                OWL.Class,
                OWL.ObjectProperty,
                OWL.DatatypeProperty,
            }:
                _profile_fail("UNSUPPORTED_OWL")
            if str(term).startswith(str(RDFS)) and term not in {
                RDFS.Class,
                RDFS.subClassOf,
                RDFS.domain,
                RDFS.range,
                RDFS.label,
                RDFS.comment,
            }:
                _profile_fail("UNSUPPORTED_RDFS")
            if str(term).startswith(str(SH)):
                _profile_fail("UNSUPPORTED_SHACL")
        elif not isinstance(term, Literal):
            _profile_fail("UNSUPPORTED_BLANK_NODE")
    if p in {RDF.type, RDFS.subClassOf, RDFS.domain, RDFS.range} and not isinstance(o, URIRef):
        _profile_fail("RDF_TYPE_OBJECT_INVALID" if p == RDF.type else "RDFS_TERM_INVALID")


@dataclass(frozen=True, slots=True)
class ProfileTermOccurrence:
    term: object
    value: object
    ordinal: int
    span: None = None


@dataclass(frozen=True, slots=True, weakref_slot=True)
class ProfileTermContext:
    """Issued local parse/view context, not source or producer authorization."""

    graph: Graph
    terms: object
    occurrences: tuple
    disabled_rule_ids: tuple
    _triples: frozenset

    def validate_graph(self, graph):
        entry = _require_context(self)
        _validate_context_values(entry)
        try:
            valid = (
                graph is self.graph
                and len(graph) <= _PROFILE_TRIPLES
                and frozenset(graph) == self._triples
            )
        except (AttributeError, TypeError, ValueError):
            valid = False
        if not valid:
            _profile_fail("PROFILE_CONTEXT_INVALID")
        return self

    def work_costs(self):
        """Issuer's immutable (preparation, full validation, maximum lookup)."""
        return _require_context(self)[8]

    def term_input(self, term):
        entry = _require_context(self)
        _node_identity(term)
        node = canonical_string(term)
        values = self.terms.get(node)
        if values:
            value = values[0]
            _validate_value(entry[6], value, node)
            return value
        # A finite RDFS closure can introduce IRIs, never new literal values.
        # Construct from the actual node with no invented source/occurrence.
        if not isinstance(term, URIRef):
            _profile_fail("PROFILE_CONTEXT_INVALID")
        return _term_input(term)


def _require_context(context):
    entry = _CONTEXTS.get(id(context))
    if type(context) is not ProfileTermContext or entry is None or entry[0]() is not context:
        _profile_fail("PROFILE_CONTEXT_INVALID")
    try:
        valid = (
            context.graph is entry[1]
            and context.terms is entry[2]
            and context.occurrences is entry[3]
            and context.disabled_rule_ids is entry[4]
            and context._triples is entry[5]
        )
    except AttributeError:
        valid = False
    if not valid:
        _profile_fail("PROFILE_CONTEXT_INVALID")
    return entry


def _native_fields(values):
    # Exact str/None values are intrinsically immutable: do not retain a mutable
    # dataclass or trust its hash/equality as a signature of its own contents.
    result = tuple(values)
    if any(value is not None and type(value) is not str for value in result):
        _profile_fail("PROFILE_CONTEXT_INVALID")
    return result


def _value_fields(value):
    from ontolearn_engine.quality.rule_profile import SourceRecord, TermInput

    if type(value) is not TermInput:
        _profile_fail("PROFILE_CONTEXT_INVALID")
    try:
        fields = _native_fields(
            (value.kind, value.lexical_form, value.datatype_iri, value.language_raw)
        )
        if fields[0] not in ("iri", "literal") or fields[1] is None:
            _profile_fail("PROFILE_CONTEXT_INVALID")
        source = value.source
        if source is None:
            source_fields = None
        else:
            if type(source) is not SourceRecord:
                _profile_fail("PROFILE_CONTEXT_INVALID")
            source_fields = _native_fields(
                (source.reference, source.digest, source.revision, source.text)
            )
    except AttributeError:
        _profile_fail("PROFILE_CONTEXT_INVALID")
    return fields, source, source_fields


def _identity_fields(kind, lexical, datatype, language):
    if kind == "iri":
        if datatype is not None or language is not None:
            _profile_fail("PROFILE_CONTEXT_INVALID")
        return kind, lexical
    effective = datatype or str(RDF.langString if language is not None else XSD.string)
    return kind, lexical, effective, language.lower() if language is not None else None


def _node_identity(term):
    if not isinstance(term, URIRef | Literal) or len(term) > 16384:
        _profile_fail("PROFILE_CONTEXT_INVALID")
    if isinstance(term, URIRef):
        return "iri", str(term)
    try:
        datatype, language = term.datatype, term.language
    except AttributeError:
        _profile_fail("PROFILE_CONTEXT_INVALID")
    if datatype is not None and (not isinstance(datatype, URIRef) or len(datatype) > 16384):
        _profile_fail("PROFILE_CONTEXT_INVALID")
    if language is not None and (type(language) is not str or len(language) > 16384):
        _profile_fail("PROFILE_CONTEXT_INVALID")
    return _identity_fields(
        "literal", str(term), str(datatype) if datatype is not None else None, language
    )


def _value_snapshot(value, node):
    fields, source, source_fields = _value_fields(value)
    identity = _identity_fields(*fields)
    if identity != _node_identity(node):
        _profile_fail("PROFILE_CONTEXT_INVALID")
    return value, fields, source, source_fields, identity


def _same_native_fields(actual, saved):
    if actual is None or saved is None:
        return actual is saved
    return len(actual) == len(saved) and all(a is b for a, b in zip(actual, saved, strict=True))


def _value_work(fields):
    # Native field/source identity checks are constant work. Only RDF identity
    # construction/language lowering scans term fields; source text is not read.
    return 256 + 8 * sum(len(field) for field in fields if field is not None)


def _validate_value(snapshots, value, node):
    saved = snapshots.get(id(value))
    if saved is None or saved[0] is not value:
        _profile_fail("PROFILE_CONTEXT_INVALID")
    fields, source, source_fields = _value_fields(value)
    if (
        not _same_native_fields(fields, saved[1])
        or source is not saved[2]
        or not _same_native_fields(source_fields, saved[3])
        or _identity_fields(*fields) != saved[4]
        or _node_identity(node) != saved[4]
    ):
        _profile_fail("PROFILE_CONTEXT_INVALID")


def _validate_context_values(entry):
    # One complete entry scan; term_input only checks its one indexed value.
    for node, values in entry[2].items():
        for value in values:
            _validate_value(entry[6], value, node)
    for saved in entry[7]:
        occurrence, node, value, ordinal = saved
        try:
            valid = (
                occurrence.term is node
                and occurrence.value is value
                and type(occurrence.ordinal) is int
                and occurrence.ordinal == ordinal
                and occurrence.span is None
            )
        except AttributeError:
            valid = False
        if not valid:
            _profile_fail("PROFILE_CONTEXT_INVALID")
        _validate_value(entry[6], value, node)


def _disabled_ids(values):
    if type(values) not in {tuple, list} or len(values) > 100:
        _profile_fail("INVALID_RULE")
    result = []
    for identity in values:
        _utf8_bound(identity, 16384)
        if not identity or identity in result:
            _profile_fail("INVALID_RULE")
        result.append(identity)
    return tuple(sorted(result))


def _issue_context(graph, terms, occurrences, disabled_rule_ids=(), *, previous=None):
    context = ProfileTermContext(
        graph, terms, occurrences, _disabled_ids(disabled_rule_ids), frozenset(graph)
    )
    key = id(context)

    def expire(reference):
        if _CONTEXTS.get(key, (None,))[0] is reference:
            _CONTEXTS.pop(key, None)

    snapshots = {}
    checked_sources = {}
    # Costs cover this extra issuer/consistency machinery, not Turtle parsing,
    # graph matching, or T05 parse_value/encoding (which keep their own charges).
    preparation_work = 128 + 8 * len(graph) + 16 * len(occurrences)
    validation_work = 64 + 8 * len(graph) + 8 * len(occurrences)
    maximum_lookup_work = 32
    for node, values in terms.items():
        for value in values:
            saved = _value_snapshot(value, node)
            if saved[2] is not None:
                source_key = id(saved[2])
                checked = checked_sources.get(source_key)
                if checked is None:
                    for field in saved[3]:
                        if field is not None:
                            _utf8_bound(field, 65536)
                    checked_sources[source_key] = saved[2], saved[3]
                    preparation_work += 64 + 4 * sum(
                        len(field) for field in saved[3] if field is not None
                    )
                elif checked[0] is not saved[2] or not _same_native_fields(checked[1], saved[3]):
                    _profile_fail("PROFILE_CONTEXT_INVALID")
            work = _value_work(saved[1])
            preparation_work += 32 + work
            validation_work += work
            maximum_lookup_work = max(maximum_lookup_work, work)
            existing = snapshots.setdefault(id(value), saved)
            if existing[0] is not value or existing[4] != saved[4]:
                _profile_fail("PROFILE_CONTEXT_INVALID")
    occurrence_snapshots = []
    for ordinal, occurrence in enumerate(occurrences):
        if (
            type(occurrence) is not ProfileTermOccurrence
            or type(occurrence.ordinal) is not int
            or occurrence.ordinal != ordinal
            or occurrence.span is not None
        ):
            _profile_fail("PROFILE_CONTEXT_INVALID")
        _validate_value(snapshots, occurrence.value, occurrence.term)
        work = _value_work(snapshots[id(occurrence.value)][1])
        preparation_work += 16 + work
        validation_work += work
        occurrence_snapshots.append((occurrence, occurrence.term, occurrence.value, ordinal))
    if previous is not None:
        old_preparation, old_validation, _ = _require_context(previous)[8]
        preparation_work += old_preparation + old_validation
    costs = preparation_work, validation_work, maximum_lookup_work
    _CONTEXTS[key] = (
        ref(context, expire),
        graph,
        terms,
        occurrences,
        context.disabled_rule_ids,
        context._triples,
        snapshots,
        tuple(occurrence_snapshots),
        costs,
    )
    return context


def bind_profile_disabled_rules(context, disabled_rule_ids):
    _require_context(context)
    context.validate_graph(context.graph)
    return _issue_context(
        context.graph, context.terms, context.occurrences, disabled_rule_ids, previous=context
    )


class _ProfileSink(LexicalSink):
    def __init__(self, graph, source):
        super().__init__(graph)
        self.source = source
        self.scalar_bytes = 0
        self.terms = {}
        self.occurrences = []

    def capture(self, term, value=None):
        if len(self.occurrences) >= _PROFILE_OCCURRENCES:
            _profile_fail("GRAPH_INPUT_LIMIT")
        value = value if value is not None else _term_input(term, self.source)
        # This is an allocation guard, not a second mechanism Budget. The core
        # owns parse_value/signing and its one shared graph-entry budget.
        size = sum(
            len(_utf8_bound(field, 16384))
            for field in (value.lexical_form, value.datatype_iri, value.language_raw)
            if field is not None
        )
        if self.scalar_bytes + size > 262144:
            _profile_fail("TEXT_INPUT_LIMIT")
        self.scalar_bytes += size
        canonical = canonical_string(term)
        self.terms.setdefault(canonical, []).append(value)
        self.occurrences.append(ProfileTermOccurrence(canonical, value, len(self.occurrences)))
        return canonical

    def newSymbol(self, *args):
        return self.capture(URIRef(validate_profile_iri(args[0])))

    def newLiteral(self, text, datatype, language):
        # Capture decoded parser fields before RDFLib lowercases/merges language
        # identities or canonical_string merges plain/explicit xsd:string.
        _utf8_bound(text, 16384)
        term = Literal(text, datatype=datatype, lang=language, normalize=False)
        value = _term_input(term, self.source, datatype=datatype, language=language, lexical=text)
        return self.capture(term, value)

    def newBlankNode(self, *args, **kwargs):
        _profile_fail("UNSUPPORTED_BLANK_NODE")

    def makeStatement(self, quadruple, why=None):
        f, p, s, o = quadruple
        triple = tuple(self.normalise(f, term) for term in (s, p, o))
        _profile_vocabulary(triple)
        super().makeStatement(quadruple, why)
        if len(self.graph) > _PROFILE_TRIPLES:
            _profile_fail("GRAPH_INPUT_LIMIT")


class _ProfileParser(LexicalSinkParser):
    def verb(self, argstr, i, res):
        from rdflib.plugins.parsers.notation3 import RDF_type

        count = len(res)
        end = super().verb(argstr, i, res)
        for index in range(count, len(res)) if end >= 0 else ():
            direction, predicate = res[index]
            # The Turtle shorthand "a" bypasses newSymbol in the pinned parser.
            if predicate == RDF_type:
                res[index] = (direction, self._store.capture(RDF.type))
        return end

    def nodeOrLiteral(self, argstr, i, res):
        from rdflib.plugins.parsers.notation3 import (
            decimal_syntax,
            exponent_syntax,
            integer_syntax,
        )

        # The pinned grammar's numeric tokens, without first coercing to host
        # int/Decimal/float (which may reject legal profile lexical values).
        state = self.lines, self.startOfLine
        start = self.skipSpace(argstr, i)
        if start >= 0 and argstr[start : start + 1] in "+-0123456789.":
            for pattern, datatype in (
                (exponent_syntax, XSD.double),
                (decimal_syntax, XSD.decimal),
                (integer_syntax, XSD.integer),
            ):
                match = pattern.match(argstr, start)
                if match is not None:
                    raw = argstr[start : match.end()]
                    _utf8_bound(raw, 16384)
                    term = Literal(raw, datatype=datatype, normalize=False)
                    res.append(self._store.capture(term))
                    return match.end()
        self.lines, self.startOfLine = state
        count, events = len(res), len(self._store.occurrences)
        end = super().nodeOrLiteral(argstr, i, res)
        for index in range(count, len(res)) if end >= 0 else ():
            term = res[index]
            if type(term) is bool:
                term = Literal("true" if term else "false", datatype=XSD.boolean, normalize=False)
                res[index] = term
            # Typed/string literals were captured by newLiteral. Bare numeric
            # tokens were recovered by the legacy parser without a sink call.
            if isinstance(term, Literal) and len(self._store.occurrences) == events:
                res[index] = self._store.capture(term)
        return end


def _profile_source(source, raw):
    from ontolearn_engine.quality.rule_profile import SourceRecord

    digest = sha256(raw).hexdigest()
    if source is None:
        return SourceRecord(digest=digest)
    if type(source) is not SourceRecord:
        _profile_fail("PROFILE_CONTEXT_INVALID")
    if source.digest is not None and source.digest != digest:
        _profile_fail("PROFILE_CONTEXT_INVALID")
    if source.text is not None and _utf8_bound(source.text, 65536) != raw:
        _profile_fail("PROFILE_CONTEXT_INVALID")
    for field in (source.reference, source.revision):
        if field is not None:
            _utf8_bound(field, 65536)
    return SourceRecord(source.reference, digest, source.revision, source.text)


def parse_profile_graph(text, *, base_uri, source=None):
    """Parse actual Turtle; preserve all term occurrences with unknown spans.

    Relative Turtle references resolve against the explicitly supplied valid
    base; resulting RDF IRIs require a scheme and may include a fragment.
    Source references/revisions remain caller context, never authorization.
    This supplies lexical input, not validated ProfileValue. The calculation
    core must apply parse_value once using its shared bounded graph-entry Budget.
    """
    from ontolearn_engine.semantic_offline import SemanticError, offline

    raw = _utf8_bound(text)
    validate_profile_iri(base_uri)
    graph = Graph()
    sink = _ProfileSink(graph, _profile_source(source, raw))
    with offline():
        try:
            parser = _ProfileParser(sink, baseURI=base_uri, turtle=True)
            parser.loadBuf(text)
        except SemanticError:
            raise
        except Exception as error:
            from ontolearn_engine.quality.rule_profile import ProfileFailure

            if isinstance(error, ProfileFailure):
                raise
            raise SemanticError("INVALID_TURTLE") from None
    for prefix, namespace in parser._bindings.items():
        graph.bind(prefix, namespace)
    terms = MappingProxyType({term: tuple(values) for term, values in sink.terms.items()})
    return graph, _issue_context(graph, terms, tuple(sink.occurrences))


def profile_context_for_graph(graph, *, disabled_rule_ids=()):
    """Validate a raw in-memory graph; no claim of pre-Graph raw/source recovery."""
    from rdflib.plugins.stores.memory import Memory

    from ontolearn_engine.semantic_offline import offline

    if type(graph) is not Graph or type(graph.store) is not Memory:
        _profile_fail("IN_MEMORY_GRAPH_REQUIRED")
    if len(graph) > _PROFILE_TRIPLES:
        _profile_fail("GRAPH_INPUT_LIMIT")
    sink = _ProfileSink(Graph(), None)
    with offline():
        for triple in graph:
            _profile_vocabulary(triple)
            for term in triple:
                sink.capture(term)
    # There is no source order to recover from a Graph. Sort bounded captured
    # fields, never pretend this stable ordinal is an original text position.
    # The calculation caller must precharge ordering to its graph work pool.
    ordered = sorted(
        sink.occurrences,
        key=lambda occurrence: (
            occurrence.value.kind,
            occurrence.value.lexical_form,
            occurrence.value.datatype_iri or "",
            occurrence.value.language_raw or "",
        ),
    )
    occurrences = tuple(
        ProfileTermOccurrence(item.term, item.value, ordinal)
        for ordinal, item in enumerate(ordered)
    )
    values_by_term = {}
    for item in occurrences:
        values_by_term.setdefault(item.term, []).append(item.value)
    terms = MappingProxyType({term: tuple(values) for term, values in values_by_term.items()})
    return _issue_context(graph, terms, occurrences, disabled_rule_ids)


def _profile_record_node(value):
    from ontolearn_engine.quality.rule_profile import SourceRecord, TermInput

    # These are raw caller records, not already-issued context values. Reject
    # their input shape here; issuer corruption retains its Internal boundary.
    try:
        if (
            type(value) is not TermInput
            or type(value.kind) is not str
            or value.kind not in ("iri", "literal")
            or type(value.lexical_form) is not str
            or any(
                field is not None and type(field) is not str
                for field in (value.datatype_iri, value.language_raw)
            )
        ):
            _profile_fail("RDF_TERM_INVALID")
        source = value.source
        if source is not None and (
            type(source) is not SourceRecord
            or any(
                field is not None and type(field) is not str
                for field in (source.reference, source.digest, source.revision, source.text)
            )
        ):
            _profile_fail("RDF_TERM_INVALID")
    except AttributeError:
        _profile_fail("RDF_TERM_INVALID")
    fields, _, _ = _value_fields(value)
    kind, lexical, datatype, language = fields
    _utf8_bound(lexical, 16384)
    if kind == "iri":
        if datatype is not None or language is not None:
            _profile_fail("RDF_TERM_INVALID")
        return URIRef(validate_profile_iri(lexical))
    if datatype is not None:
        _utf8_bound(datatype, 16384)
        validate_profile_iri(datatype)
    if language is not None:
        _utf8_bound(language, 16384)
    try:
        return Literal(
            lexical,
            datatype=URIRef(datatype) if datatype is not None else None,
            lang=language,
            normalize=False,
        )
    except (TypeError, ValueError):
        _profile_fail("RDF_TERM_INVALID")


def profile_graph_from_records(records, *, disabled_rule_ids=()):
    """Adapt explicit N3/IRI-derived TermInputs, never synthesize source text.

    Each record is an exact tuple of three exact canonical TermInput objects;
    literal callers use the one strict decode_profile_term N3 entry point.
    This checks bounded RDF structure, not producer/source authenticity or
    profile value validity. The core still owns parse_value and its one Budget.
    """
    from ontolearn_engine.semantic_offline import offline

    if type(records) is not tuple:
        _profile_fail("RDF_TERM_INVALID")
    if len(records) > _PROFILE_TRIPLES:
        _profile_fail("GRAPH_INPUT_LIMIT")
    graph = Graph()
    sink = _ProfileSink(graph, None)
    with offline():
        for record in records:
            if type(record) is not tuple or len(record) != 3:
                _profile_fail("RDF_TERM_INVALID")
            nodes = tuple(sink.capture(_profile_record_node(value), value) for value in record)
            _profile_vocabulary(nodes)
            graph.add(nodes)
    terms = MappingProxyType({term: tuple(values) for term, values in sink.terms.items()})
    return graph, _issue_context(graph, terms, tuple(sink.occurrences), disabled_rule_ids)


def decode_profile_term(text):
    """Decode one exact canonical N3 term; reject injection and trailing syntax."""
    from ontolearn_engine.semantic_offline import SemanticError, offline

    _utf8_bound(text)
    if not (text.startswith("<") or text.startswith('"')):
        _profile_fail("RDF_TERM_INVALID")
    graph = Graph()
    with offline():
        try:
            SinkParser(
                LexicalSink(graph, canonical_strings=False),
                baseURI="urn:ontolearn:profile-term:",
                turtle=True,
            ).loadBuf("<urn:ontolearn:subject> <urn:ontolearn:predicate> " + text + " .")
            if len(graph) != 1:
                _profile_fail("RDF_TERM_INVALID")
            s, p, term = next(iter(graph))
            if (
                str(s) != "urn:ontolearn:subject"
                or str(p) != "urn:ontolearn:predicate"
                or not isinstance(term, URIRef | Literal)
                or term.n3() != text
            ):
                _profile_fail("RDF_TERM_INVALID")
        except SemanticError:
            raise
        except Exception:
            _profile_fail("RDF_TERM_INVALID")
        value = _term_input(term)
        return value
