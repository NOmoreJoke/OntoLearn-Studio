"""Store3 catalog extension; checkpoint/application payloads remain schema 1.

Only the original Store connection and lifetime lease migrate this catalog.
"""

import sqlite3

from ontolearn_engine.storage import canonical, digest

CATALOG_VERSION = 2
TABLES = [
    (
        "management_receipts",
        "CREATE TABLE management_receipts(operation TEXT PRIMARY KEY,"
        "sequence INTEGER NOT NULL UNIQUE CHECK(sequence>0),"
        "project TEXT NOT NULL REFERENCES projects(id),"
        "target TEXT NOT NULL REFERENCES projects(id),payload TEXT NOT NULL)",
    ),
    (
        "project_lifecycle",
        "CREATE TABLE project_lifecycle(project TEXT PRIMARY KEY REFERENCES projects(id),"
        "state TEXT NOT NULL CHECK(state IN ('active','trashed')),"
        "version INTEGER NOT NULL CHECK(version>0),"
        "operation TEXT NOT NULL REFERENCES management_receipts(operation))",
    ),
    (
        "schema_migrations",
        "CREATE TABLE schema_migrations(version INTEGER PRIMARY KEY CHECK(version=2),"
        "payload TEXT NOT NULL)",
    ),
]
TRIGGERS = [
    (
        f"immutable_{table}_{action}",
        f"CREATE TRIGGER immutable_{table}_{action} BEFORE {action} ON {table} "
        "BEGIN SELECT RAISE(ABORT,'immutable management evidence'); END",
    )
    for table in ("management_receipts", "schema_migrations")
    for action in ("UPDATE", "DELETE")
]


def catalog():
    from ontolearn_engine.project import format3

    tables = [
        (name, sql.replace("CHECK(schema_version=1)", "CHECK(schema_version=2)"))
        for name, sql in format3.TABLES
    ]
    return tables + TABLES, format3.TRIGGERS + TRIGGERS


def schema_hash():
    tables, triggers = catalog()
    return digest(tables + triggers)


def version(store):
    from ontolearn_engine.project.format3 import Format3Fault

    try:
        rows = store._db.execute("SELECT schema_version FROM app_format").fetchall()
    except sqlite3.DatabaseError:
        raise Format3Fault("structure") from None
    if len(rows) != 1 or type(rows[0][0]) is not int or rows[0][0] < 1:
        raise Format3Fault("structure")
    return rows[0][0]


def _install(store, old, backup_hash, source_hash, hook):
    from ontolearn_engine.project import format3

    db = store._db
    for action in ("UPDATE", "DELETE"):
        db.execute(f"DROP TRIGGER immutable_app_format_{action}")
    db.execute("DROP TABLE app_format")
    db.execute(catalog()[0][0][1])
    db.execute(
        "INSERT INTO app_format VALUES(1,2,?,?,?,?)",
        (schema_hash(), old["migration_id"], old["source_format"], old["backup_hash"]),
    )
    for name, sql in format3.TRIGGERS:
        if name.startswith("immutable_app_format_"):
            db.execute(sql)
    for name, sql in TABLES + TRIGGERS:
        db.execute(sql)
        hook("management_schema_ddl:" + name)
    proof = {
        "schemaMigrationVersion": 1,
        "oldCatalog": old,
        "newSchemaHash": schema_hash(),
        "backupHash": backup_hash,
        "sourceLogicalHash": source_hash,
    }
    db.execute("INSERT INTO schema_migrations VALUES(2,?)", (canonical(proof),))
    hook("management_schema_receipt")


def install_fresh(store, hook):
    old = dict(store._db.execute("SELECT * FROM app_format").fetchone())
    _install(store, old, None, None, hook)


def migrate(store, backup_path, hook):
    from ontolearn_engine.project import format3

    current = version(store)
    if current == 2:
        return
    if current != 1:
        raise format3.Format3Fault("format")
    with store._read():
        format3.validate(store, catalog_version=1)
    backup_hash, source_hash = format3.migration_backup(store, backup_path, hook)
    with store._transaction(hook):
        if format3.logical_hash(store._db) != source_hash:
            raise format3.Format3Fault("sourceChanged")
        format3.validate(store, catalog_version=1)
        old = dict(store._db.execute("SELECT * FROM app_format").fetchone())
        _install(store, old, backup_hash, source_hash, hook)
        format3.validate(store)
        hook("management_schema_validated")


def validate(store):
    from ontolearn_engine.project import format3

    require = format3._require
    rows = store._db.execute("SELECT * FROM schema_migrations").fetchall()
    require(len(rows) == 1 and rows[0]["version"] == 2)
    proof = format3._json(rows[0]["payload"])
    require(
        type(proof) is dict
        and set(proof)
        == {
            "schemaMigrationVersion",
            "oldCatalog",
            "newSchemaHash",
            "backupHash",
            "sourceLogicalHash",
        }
    )
    require(
        type(proof["schemaMigrationVersion"]) is int
        and proof["schemaMigrationVersion"] == 1
        and proof["newSchemaHash"] == schema_hash()
    )
    old = proof["oldCatalog"]
    new = dict(store._db.execute("SELECT * FROM app_format").fetchone())
    require(type(old) is dict and set(old) == set(new))
    require(old == {**new, "schema_version": 1, "schema_hash": format3.SCHEMA_HASH})
    from ontolearn_engine.project.applications import hash_ref

    require(
        (proof["backupHash"] is None and proof["sourceLogicalHash"] is None)
        or (hash_ref(proof["backupHash"]) and hash_ref(proof["sourceLogicalHash"]))
    )
    from ontolearn_engine.project.management import validate_ledger

    validate_ledger(store)
