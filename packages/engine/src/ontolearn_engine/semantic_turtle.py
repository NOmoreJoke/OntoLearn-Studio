"""Text-only Turtle parsing with local, lossless RDF literal construction.

The pinned RDFLib productions parse the text. Literal construction preserves
spelling and a Turtle statement guard rejects silently discarded orphan terms;
no process-wide normalization or parser settings are changed.
"""

from decimal import Decimal

from rdflib import XSD, Graph, Literal
from rdflib.plugins.parsers.notation3 import RDFSink, SinkParser, sfloat


class LexicalSink(RDFSink):
    def newLiteral(self, text, datatype, language):
        return Literal(text, datatype=datatype, lang=language, normalize=False)


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
