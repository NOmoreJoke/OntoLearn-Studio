"""Rebuild the bounded S1 asserted read model from normalized immutable input.

No parsing by URL, plugin discovery, remote datasets or user-supplied query here.
Full PRD ontology semantics and reasoning remain later capability work.
"""

from urllib.parse import urlsplit

from rdflib import XSD, Graph, Literal, URIRef


def iri(value: str) -> URIRef:
    if (
        not isinstance(value, str)
        or not urlsplit(value).scheme
        or any(c.isspace() or c in '<>"{}|^`\\' for c in value)
    ):
        raise ValueError("Absolute stable IRI required")
    return URIRef(value)


def term(value: str) -> URIRef | Literal:
    if value.startswith("<"):
        if not value.endswith(">"):
            raise ValueError("Malformed IRI object")
        iri(value[1:-1])
    subject, predicate = URIRef("urn:ontolearn:term"), URIRef("urn:ontolearn:value")
    try:
        parsed = Graph().parse(
            data=f"<{subject}> <{predicate}> {value} .",
            format="turtle",
            publicID="urn:ontolearn:s1:",
        )
        if len(parsed) != 1 or len(list(parsed.objects(subject, predicate))) != 1:
            raise ValueError("Object must contain exactly one RDF term")
        result = next(parsed.objects(subject, predicate))
    except Exception as error:
        raise ValueError("Unsupported S1 RDF object") from error
    if not isinstance(result, URIRef | Literal):
        raise ValueError("Only stable IRI and literal objects supported in S1")
    if isinstance(result, URIRef):
        iri(str(result))
    if isinstance(result, Literal):
        if result.datatype == XSD.string:
            return Literal(str(result))
        if result.language:
            return Literal(str(result), lang=result.language.lower())
    return result


def graph_from_snapshot(snapshot: dict) -> Graph:
    graph = Graph()
    for fact in snapshot["state"]["facts"]:
        if fact["object"] is not None:  # managed deletion tombstones are provenance, not facts
            graph.add((iri(fact["subject"]), iri(fact["predicate"]), term(fact["object"])))
    for definition in snapshot["state"]["definitions"]:
        if definition["layer"] == "ontology":
            import json

            payload = json.loads(definition["payload"])
            if isinstance(payload, dict):
                for triple in payload.get("triples", []):
                    graph.add(
                        (iri(triple["subject"]), iri(triple["predicate"]), term(triple["object"]))
                    )
    return graph
