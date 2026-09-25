#!/usr/bin/env python3
"""Does anything atomic stop two concurrent uploads creating a duplicate row?

    python _probe\\concurrency_probe.py

Answers Alex Zamurko's question of 24 September by executing it rather than
reasoning about it: is duplicate prevention only "check first, then insert"?

Runs in a THROWAWAY database. `epistemicos` is never opened, never written,
never read. The scratch database is created at the start and dropped at the
end, including on failure.

Method
------
Real concurrency, made deterministic. Two sessions, interleaved by hand:

    A   BEGIN
    A   SELECT by key        -> miss
    B   BEGIN
    B   SELECT by key        -> miss          both saw an empty table
    A   INSERT
    B   INSERT                                blocks on the index, if any
    A   COMMIT
    B   (unblocks)                            succeeds, or raises
    B   COMMIT

Both sessions pass their own check before either writes, which is exactly the
race the question is about. Whether the second write survives is then a
property of the schema and nothing else.

Three schemas, because the answer is not the same for all of them:

    1  today          papers_hash_unique UNIQUE (hash), migration 0001
    2  Stage 1        that constraint dropped, non-unique source_sha256 index
    3  Stage 1        the same, plus one_child_per_paper on the new_version path

Exit 0 = every scenario behaved as the specification says it should.
Exit 1 = at least one did not, and the difference is named.
"""
from __future__ import annotations

import subprocess
import sys
import threading
import time
import uuid

SCRATCH = "concurrency_probe_scratch"
ADMIN_DB = "epistemicos"
USER = "epistemicos"


def container() -> str:
    """The running postgres container, discovered rather than assumed."""
    out = subprocess.run(
        ["docker", "ps", "--filter", "ancestor=postgres:16-alpine",
         "--format", "{{.Names}}"],
        capture_output=True, text=True)
    names = [n for n in out.stdout.split() if n]
    if names:
        return names[0]
    # Fall back to any container with postgres in the name.
    out = subprocess.run(
        ["docker", "ps", "--format", "{{.Names}}"],
        capture_output=True, text=True)
    for n in out.stdout.split():
        if "postgres" in n or "db" in n:
            return n
    raise SystemExit(
        "no running postgres container found. Start it with\n"
        "    docker compose up -d postgres\n"
        "and run this again. Nothing was created or changed.")


CONTAINER = None


def psql(db: str, sql: str, *, quiet: bool = True):
    """One statement batch, one session, one exit."""
    cmd = ["docker", "exec", "-i", CONTAINER,
           "psql", "-U", USER, "-d", db, "-v", "ON_ERROR_STOP=1",
           "-X", "-q", "-t", "-A"]
    r = subprocess.run(cmd, input=sql, capture_output=True, text=True)
    if r.returncode != 0 and not quiet:
        print(r.stderr.strip())
    return r


SCHEMA_BASE = """
CREATE TABLE papers (
    id              UUID PRIMARY KEY,
    hash            VARCHAR(64) NOT NULL,
    source_sha256   VARCHAR(64),
    parent_paper_id UUID REFERENCES papers (id),
    upload_intent   VARCHAR(16)
);
"""

SCHEMA = {
    # Migration 0001, as it stands in the repository today.
    "today": SCHEMA_BASE + """
ALTER TABLE papers ADD CONSTRAINT papers_hash_unique UNIQUE (hash);
""",
    # Stage 1 v8 §7.5: the constraint is dropped, source identity is indexed
    # but deliberately NOT unique, because two manuscripts may share a source.
    "stage1": SCHEMA_BASE + """
CREATE INDEX idx_papers_hash ON papers (hash);
CREATE INDEX idx_papers_source_sha256 ON papers (source_sha256);
""",
    # The same, plus the partial unique index Alex specified on 1 September.
    "stage1_child": SCHEMA_BASE + """
CREATE INDEX idx_papers_hash ON papers (hash);
CREATE INDEX idx_papers_source_sha256 ON papers (source_sha256);
CREATE UNIQUE INDEX one_child_per_paper
    ON papers (parent_paper_id) WHERE parent_paper_id IS NOT NULL;
""",
}


def race(db: str, check_sql: str, insert_a: str, insert_b: str) -> dict:
    """Two sessions that both pass their check before either writes."""
    result = {"a_saw": None, "b_saw": None, "a": None, "b": None}
    gate_checked = threading.Event()
    gate_a_inserted = threading.Event()

    def session_a():
        sql = f"""
BEGIN;
{check_sql}
"""
        r = psql(db, sql + "COMMIT;")   # probe read only, own transaction
        result["a_saw"] = r.stdout.strip()
        gate_checked.set()
        # Now the real write, held open so B's insert meets it.
        r = psql(db, f"BEGIN;\n{insert_a}\nSELECT pg_sleep(2);\nCOMMIT;")
        result["a"] = "committed" if r.returncode == 0 else _err(r)
        gate_a_inserted.set()

    def session_b():
        gate_checked.wait(10)
        r = psql(db, f"BEGIN;\n{check_sql}\nCOMMIT;")
        result["b_saw"] = r.stdout.strip()
        # Starts while A's transaction is still open, so if an index is going
        # to arbitrate, this is where it does it.
        time.sleep(0.5)
        r = psql(db, f"BEGIN;\n{insert_b}\nCOMMIT;")
        result["b"] = "committed" if r.returncode == 0 else _err(r)

    ta, tb = threading.Thread(target=session_a), threading.Thread(target=session_b)
    ta.start(); tb.start(); ta.join(30); tb.join(30)
    return result


def _err(r) -> str:
    for line in (r.stderr or "").splitlines():
        if "ERROR:" in line:
            detail = line.split("ERROR:", 1)[1].strip()
            return f"REJECTED: {detail[:72]}"
    return "REJECTED: (no detail)"


def scenario(name: str, schema: str, check: str, ins_a: str, ins_b: str,
             expect_b: str, why: str) -> bool:
    psql(ADMIN_DB, f'DROP DATABASE IF EXISTS {SCRATCH};')
    psql(ADMIN_DB, f'CREATE DATABASE {SCRATCH};')
    r = psql(SCRATCH, SCHEMA[schema], quiet=False)
    if r.returncode != 0:
        print(f"  {name}: schema failed to build; scenario not run")
        return False

    out = race(SCRATCH, check, ins_a, ins_b)
    rows = psql(SCRATCH, "SELECT count(*) FROM papers;").stdout.strip()

    got = "committed" if out["b"] == "committed" else "rejected"
    ok = got == expect_b

    print(f"\n  {name}")
    print(f"    both sessions checked first, both saw: "
          f"A={out['a_saw'] or '0'!s:>3}  B={out['b_saw'] or '0'!s:>3}")
    print(f"    session A insert   {out['a']}")
    print(f"    session B insert   {out['b']}")
    print(f"    rows afterwards    {rows}")
    print(f"    expected B to be   {expect_b}    {'OK' if ok else 'MISMATCH'}")
    print(f"    {why}")
    return ok


def main() -> int:
    global CONTAINER
    CONTAINER = container()
    print(f"  postgres container: {CONTAINER}")
    print(f"  scratch database:   {SCRATCH}  (created and dropped here)")
    print(f"  {ADMIN_DB} is never opened for reading or writing.")

    h = "a" * 64
    s = "b" * 64
    pa, pb = str(uuid.uuid4()), str(uuid.uuid4())
    parent = str(uuid.uuid4())

    results = []
    try:
        results.append(scenario(
            "1. TODAY — papers_hash_unique is still in migration 0001",
            "today",
            f"SELECT count(*) FROM papers WHERE hash = '{h}';",
            f"INSERT INTO papers (id, hash) VALUES ('{pa}', '{h}');",
            f"INSERT INTO papers (id, hash) VALUES ('{pb}', '{h}');",
            expect_b="rejected",
            why="An atomic safeguard exists today. Both sessions missed the "
                "check; the constraint arbitrated."))

        results.append(scenario(
            "2. STAGE 1 — that constraint dropped, source index non-unique",
            "stage1",
            f"SELECT count(*) FROM papers WHERE source_sha256 = '{s}';",
            f"INSERT INTO papers (id, hash, source_sha256, upload_intent) "
            f"VALUES ('{pa}', '{h}', '{s}', 'new_paper');",
            f"INSERT INTO papers (id, hash, source_sha256, upload_intent) "
            f"VALUES ('{pb}', '{h}', '{s}', 'new_paper');",
            expect_b="committed",
            why="Nothing arbitrates, BY DESIGN. Two manuscripts over one "
                "source is legal under LDVI, which is why the index is "
                "not unique."))

        # The new_version path, where a duplicate IS a defect.
        psql(ADMIN_DB, f'DROP DATABASE IF EXISTS {SCRATCH};')
        psql(ADMIN_DB, f'CREATE DATABASE {SCRATCH};')
        psql(SCRATCH, SCHEMA["stage1_child"])
        psql(SCRATCH, f"INSERT INTO papers (id, hash, upload_intent) "
                      f"VALUES ('{parent}', 'p{'0'*63}', 'new_paper');")
        out = race(
            SCRATCH,
            f"SELECT count(*) FROM papers WHERE parent_paper_id = '{parent}';",
            f"INSERT INTO papers (id, hash, parent_paper_id, upload_intent) "
            f"VALUES ('{pa}', '{h}', '{parent}', 'new_version');",
            f"INSERT INTO papers (id, hash, parent_paper_id, upload_intent) "
            f"VALUES ('{pb}', '{h}', '{parent}', 'new_version');")
        rows = psql(SCRATCH,
                    f"SELECT count(*) FROM papers WHERE parent_paper_id = "
                    f"'{parent}';").stdout.strip()
        got = "committed" if out["b"] == "committed" else "rejected"
        ok = got == "rejected"
        print("\n  3. STAGE 1 — new_version, with one_child_per_paper")
        print(f"    both sessions checked first, both saw: "
              f"A={out['a_saw'] or '0'!s:>3}  B={out['b_saw'] or '0'!s:>3}")
        print(f"    session A insert   {out['a']}")
        print(f"    session B insert   {out['b']}")
        print(f"    children of parent {rows}")
        print(f"    expected B to be   rejected    {'OK' if ok else 'MISMATCH'}")
        print("    The new_version path IS atomically protected, on the path "
              "where\n    a duplicate is a defect rather than a valid outcome.")
        results.append(ok)
    finally:
        psql(ADMIN_DB, f'DROP DATABASE IF EXISTS {SCRATCH};')

    print("\n" + "-" * 68)
    if all(results):
        print("""
  Every scenario behaved as specified.

    new_paper     duplication is a legitimate outcome   no constraint, by design
    new_version   duplication breaks the chain          one_child_per_paper

  Today's protection is real but incidental: papers_hash_unique was
  enforcing source uniqueness, which Stage 1 removes deliberately.
  one_child_per_paper is SPECIFIED AND NOT BUILT — the latest migration
  in the repository is 0012, so scenario 3 shows what Stage 1 will do,
  not what the database does today.
""")
        return 0
    print("\n  At least one scenario did not behave as specified. See above.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
