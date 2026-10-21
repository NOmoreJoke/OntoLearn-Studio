"""Pinned SPARQL grammar copied per call to preserve numeric token spelling."""

from copy import deepcopy

from pyparsing import MatchFirst, Regex
from rdflib import XSD, Literal
from rdflib.plugins.sparql import algebra, operators, parser
from rdflib.plugins.sparql.parserutils import CompValue, Expr

from ontolearn_engine.semantic_offline import SemanticError
from ontolearn_engine.semantic_turtle import canonical_string


def _literal_action(datatype, sign=""):
    # Exactly one argument: pyparsing inspects callable arity.
    def action(tokens):
        return Literal(sign + str(tokens[0]), datatype=datatype, normalize=False)

    return action


def _clone_grammar():
    memo = {}
    grammar = deepcopy(parser.Query, memo)
    nodes, seen, pending = [], set(), [grammar]
    while pending:
        node = pending.pop()
        if id(node) in seen:
            continue
        seen.add(id(node))
        nodes.append(node)
        pending.extend(node.recurse())
    patterns = {
        parser.INTEGER.pattern: XSD.integer,
        parser.DECIMAL.pattern: XSD.decimal,
        parser.DOUBLE.pattern: XSD.double,
    }
    counts = dict.fromkeys(patterns.values(), 0)
    for node in nodes:
        if isinstance(node, Regex) and node.pattern in patterns:
            datatype = patterns[node.pattern]
            node.set_parse_action(_literal_action(datatype))
            counts[datatype] += 1
    if sorted(counts.values()) != [3, 3, 3]:
        raise RuntimeError("UNPROVED_LOCAL_NUMERIC_GRAMMAR")
    for name, datatype in (
        ("INTEGER", XSD.integer),
        ("DECIMAL", XSD.decimal),
        ("DOUBLE", XSD.double),
    ):
        for suffix, sign in (("POSITIVE", "+"), ("NEGATIVE", "-")):
            original = getattr(parser, name + "_" + suffix)
            clone = memo.get(id(original))
            if clone is None or clone is original:
                raise RuntimeError("UNPROVED_LOCAL_SIGN_GRAMMAR")
            clone.set_parse_action(_literal_action(datatype, sign))
    # SPARQL longest-match chooses an adjacent signed numeric token before a
    # unary operator. The library instead tries UnaryPlus/Minus first, losing
    # spelling even when the numeric leaf itself is lossless (STR(-01) -> -1).
    # The library's normal streamline optimization can remove the nested
    # PrimaryExpression wrapper. Both pinned shapes flatten to the same 81
    # choices: three unary operators followed by 78 primary alternatives.
    unary = parser.UnaryExpression
    clone = memo.get(id(unary))

    def choices(node):
        # MatchFirst wrappers with actions/names are semantic: notably Var
        # constructs an RDF Variable. Preserve them just as streamline does.
        if (
            isinstance(node, MatchFirst)
            and not node.parseAction
            and not node.resultsName
            and not node.debug
        ):
            return [leaf for child in node.exprs for leaf in choices(child)]
        return [node]

    alternatives = choices(clone) if isinstance(clone, MatchFirst) else []
    if (
        not isinstance(unary, MatchFirst)
        or clone is unary
        or len(alternatives) != 81
        or [node.name for node in alternatives[:3]] != ["UnaryNot", "UnaryPlus", "UnaryMinus"]
        or any(node.name in {"UnaryNot", "UnaryPlus", "UnaryMinus"} for node in alternatives[3:])
    ):
        raise RuntimeError("UNPROVED_LOCAL_UNARY_GRAMMAR")
    clone.exprs = alternatives[3:] + alternatives[:3]
    return grammar


def _canonical_query_strings(prepared):
    """Normalize only this private query, including runtime-created strings.

    VALUES contains ordinary dictionaries, so RDFLib's CompValue-only traversal
    would miss its constants. Expr.eval itself remains untouched: it owns ctx
    lifetime and SPARQLError semantics. Each instance's original bound callback
    retains both, while its returned string uses the graph's term identity.
    """
    seen = set()

    def visit(value):
        if isinstance(value, Literal):
            return canonical_string(value)
        # translateQuery inserts this shared module singleton for OPTIONAL
        # without a filter. Never install callbacks or ctx on that global Expr.
        if value is operators.TrueFilter:
            evaluate = vars(value).get("_evalfn")
            if getattr(evaluate, "__self__", None) is not value or not callable(
                getattr(evaluate, "__func__", None)
            ):
                raise RuntimeError("UNPROVED_LOCAL_TRUE_FILTER")
            value = Expr(value.name, evaluate.__func__, **dict(value.items()))
        if isinstance(value, CompValue):
            if id(value) in seen:
                return value
            seen.add(id(value))
            for key, child in list(value.items()):
                value[key] = visit(child)
            if isinstance(value, Expr):
                evaluate = vars(value).get("_evalfn")
                if evaluate is not None:
                    if (
                        not callable(evaluate)
                        or getattr(evaluate, "__self__", None) is not value
                        or not callable(getattr(evaluate, "__func__", None))
                    ):
                        raise RuntimeError("UNPROVED_LOCAL_EXPRESSION_CALLBACK")

                    def evaluate_string(ctx, original=evaluate):
                        return canonical_string(original(ctx))

                    value._evalfn = evaluate_string
            return value
        if isinstance(value, dict):
            return {key: visit(child) for key, child in value.items()}
        if isinstance(value, list):
            return [visit(child) for child in value]
        if isinstance(value, tuple):
            return tuple(visit(child) for child in value)
        return value

    prepared.algebra = visit(prepared.algebra)
    return prepared


def prepare_lexical_query(text):
    # A topology/deepcopy failure is an internal implementation failure, never
    # a user syntax error. Do not catch it in the parse/translation adapter.
    grammar = _clone_grammar()
    try:
        tree = grammar.parse_string(parser.expandUnicodeEscapes(text), parse_all=True)
        prepared = algebra.translateQuery(tree)
    except Exception as error:
        raise SemanticError("INVALID_QUERY") from error
    # A local adaptation failure is internal, never user query syntax.
    return _canonical_query_strings(prepared)
