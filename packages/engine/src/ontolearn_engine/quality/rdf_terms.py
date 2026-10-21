"""Use the approved RDF term parser without emitting rejected lexical values.

RDFLib logs ill-typed literal conversions before returning Literal. The context
filter suppresses only that parser's diagnostics inside this local validation;
other threads/tasks and normal engine logging retain their existing behavior.
"""

import logging
from contextvars import ContextVar

from ontolearn_engine.rdf_snapshot import term

_parsing = ContextVar("t05_validating_rdf_term", default=False)


class _ParserDiagnosticFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        return not _parsing.get()


logging.getLogger("rdflib.term").addFilter(_ParserDiagnosticFilter())


def private_term(value: str):
    token = _parsing.set(True)
    try:
        return term(value)
    finally:
        _parsing.reset(token)
