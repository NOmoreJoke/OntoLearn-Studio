"""Private T05 helpers. Pure profile imports do not install RDF parser policy."""

__all__ = ["DefinitionError", "ValidatedDefinition", "build_plan", "validate_definition"]


def __getattr__(name):
    if name in ("DefinitionError", "ValidatedDefinition", "validate_definition"):
        from . import definitions

        value = getattr(definitions, name)
    elif name == "build_plan":
        from .planning import build_plan

        value = build_plan
    else:
        raise AttributeError(name)
    globals()[name] = value
    return value
