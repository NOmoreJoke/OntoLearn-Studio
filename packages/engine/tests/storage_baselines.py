"""Prepared PRD G fixtures and E.5 expected rounds; not a behavior simulator."""

from ontolearn_engine.rdf_snapshot import term
from ontolearn_engine.storage import canonical, digest


def statement(subject, predicate, value):
    if value.startswith("urn:"):
        value = f"<{value}>"
    value = term(value).n3()
    return {
        "id": digest([subject, predicate, value]),
        "subject": subject,
        "predicate": predicate,
        "object": value,
    }


def g_definitions(behavior=False):
    definitions = [
        {
            "layer": "ontology",
            "id": "G",
            "value": {
                "classes": ["Equipment", "Alarm", "WorkOrder", "HighRiskEquipment"],
                "properties": ["name", "level", "status", "alarm", "workOrderStatus", "eventOrder"],
            },
        },
        {
            "layer": "constraint",
            "id": "name",
            "value": {
                "target": "Equipment",
                "path": "name",
                "minCount": 1,
                "scope": "asserted",
            },
        },
        {
            "layer": "rule",
            "id": "R-risk",
            "value": {
                "condition": "Equipment with High/Open Alarm",
                "output": "HighRiskEquipment",
            },
        },
        {
            "layer": "behavior",
            "id": "B-risk",
            "value": {
                "condition": "new High/Open Alarm and HighRiskEquipment",
                "action": "create linked pending WorkOrder",
                "enabled": True,
                "priority": 0,
            },
        },
        {"layer": "scenario", "id": "initial", "value": {"pendingEvents": [], "orders": []}},
    ]
    if behavior:
        definitions.extend(
            [
                {
                    "layer": "ontology",
                    "id": "test",
                    "value": {
                        "classes": ["TestObject", "Notification"],
                        "properties": {
                            "P": {"type": "boolean", "single": True},
                            "notificationEvent": {},
                            "workOrderStatus": {"single": True},
                        },
                    },
                },
                *[
                    {"layer": "behavior", "id": identity, "value": value}
                    for identity, value in {
                        "B-a": {"event": "工单竞争触发", "writes": {"W-test": "S-a"}},
                        "B-b": {"event": "工单竞争触发", "writes": {"W-test": "S-b"}},
                        "B-multi": {
                            "event": "多目标触发",
                            "actions": ["write payload target/value", "notify event"],
                        },
                        "X": {
                            "event": "E-B06",
                            "priority": 0,
                            "enabled": True,
                            "actions": ["T1.P=true"],
                        },
                        "Y": {
                            "event": "E-B06",
                            "priority": 0,
                            "enabled": True,
                            "condition": "T1.P=false",
                            "actions": ["notify E-B06"],
                        },
                        "B-probe": {
                            "event": "E-probe",
                            "condition": "001 HighRiskEquipment",
                            "actions": ["notify E-probe"],
                        },
                    }.items()
                ],
                {
                    "layer": "scenario",
                    "id": "behavior-test",
                    "value": {
                        "maxRounds": 1,
                        "capacity": 0,
                        "pendingEvents": [],
                    },
                },
            ]
        )
    return definitions


def g_facts(behavior=False):
    facts = []
    for identity, name in (("001", "泵站A"), ("002", "泵站B"), ("003", "备用泵C")):
        facts.extend(
            [
                statement(f"urn:equipment/{identity}", "urn:type", "urn:Equipment"),
                statement(f"urn:equipment/{identity}", "urn:name", canonical(name)),
            ]
        )
    for identity, equipment, level, status in (
        ("A01", "001", "High", "Open"),
        ("A02", "002", "High", "Closed"),
        ("A03", "003", "Low", "Open"),
    ):
        alarm = f"urn:alarm/{identity}"
        facts.extend(
            [
                statement(alarm, "urn:type", "urn:Alarm"),
                statement(alarm, "urn:level", canonical(level)),
                statement(alarm, "urn:status", canonical(status)),
                statement(f"urn:equipment/{equipment}", "urn:alarm", alarm),
            ]
        )
    if behavior:
        facts.extend(
            [
                statement("urn:T1", "urn:type", "urn:TestObject"),
                statement("urn:T1", "urn:P", "false"),
            ]
        )
        for order in ("W-test", "W-other"):
            facts.extend(
                [
                    statement(f"urn:{order}", "urn:type", "urn:WorkOrder"),
                    statement(f"urn:{order}", "urn:workOrderStatus", '"待处理"'),
                ]
            )
    return facts


# Literal complete sets copied from E.5, never computed by a pretend simulator.
E5 = {
    3: [
        {
            "created": ["W001", "W002", "W003", "W004"],
            "completed": ["W001", "W002", "W003"],
            "backlog": ["W004"],
            "backlogCount": 1,
            "completedCount": 3,
        },
        {
            "created": ["W005", "W006", "W007", "W008"],
            "completed": ["W004", "W005", "W006"],
            "backlog": ["W007", "W008"],
            "backlogCount": 2,
            "completedCount": 6,
        },
        {
            "created": ["W009", "W010", "W011", "W012"],
            "completed": ["W007", "W008", "W009"],
            "backlog": ["W010", "W011", "W012"],
            "backlogCount": 3,
            "completedCount": 9,
        },
        {
            "created": ["W013", "W014", "W015", "W016"],
            "completed": ["W010", "W011", "W012"],
            "backlog": ["W013", "W014", "W015", "W016"],
            "backlogCount": 4,
            "completedCount": 12,
        },
    ],
    4: [
        {
            "created": ["W001", "W002", "W003", "W004"],
            "completed": ["W001", "W002", "W003", "W004"],
            "backlog": [],
            "backlogCount": 0,
            "completedCount": 4,
        },
        {
            "created": ["W005", "W006", "W007", "W008"],
            "completed": ["W005", "W006", "W007", "W008"],
            "backlog": [],
            "backlogCount": 0,
            "completedCount": 8,
        },
        {
            "created": ["W009", "W010", "W011", "W012"],
            "completed": ["W009", "W010", "W011", "W012"],
            "backlog": [],
            "backlogCount": 0,
            "completedCount": 12,
        },
        {
            "created": ["W013", "W014", "W015", "W016"],
            "completed": ["W013", "W014", "W015", "W016"],
            "backlog": [],
            "backlogCount": 0,
            "completedCount": 16,
        },
    ],
}
