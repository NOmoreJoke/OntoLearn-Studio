"""Pinned SPARQL grammar copied per call to preserve numeric token spelling."""

from copy import deepcopy

from pyparsing import MatchFirst, Regex
from rdflib import XSD, Literal
from rdflib.plugins.sparql import algebra, parser

from ontolearn_engine.semantic_offline import SemanticError


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


def prepare_lexical_query(text):
    # A topology/deepcopy failure is an internal implementation failure, never
    # a user syntax error. Do not catch it in the parse/translation adapter.
    grammar = _clone_grammar()
    try:
        tree = grammar.parse_string(parser.expandUnicodeEscapes(text), parse_all=True)
        return algebra.translateQuery(tree)
    except Exception as error:
        raise SemanticError("INVALID_QUERY") from error
