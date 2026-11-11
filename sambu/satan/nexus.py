"""SQLite-backed Nexus registry, event inbox, and threat memory."""
from __future__ import annotations
import json, sqlite3, time
from pathlib import Path
from typing import Mapping
from .mesh import MeshEnvelope, MeshError, verify_envelope

class Nexus:
    """Small durable control-plane store; network serving is provided by adapters."""
    def __init__(self, database: str | Path = ":memory:") -> None:
        self.database = str(database)
        self._db = sqlite3.connect(self.database)
        self._db.row_factory = sqlite3.Row
        self._db.execute("PRAGMA foreign_keys=ON")
        self._db.executescript("""
            CREATE TABLE IF NOT EXISTS repositories (
                repo_id TEXT PRIMARY KEY, default_branch TEXT NOT NULL,
                metadata_json TEXT NOT NULL, registered_at INTEGER NOT NULL
            );
            CREATE TABLE IF NOT EXISTS events (
                event_id TEXT PRIMARY KEY, origin TEXT NOT NULL, kind TEXT NOT NULL,
                digest TEXT NOT NULL, payload_json TEXT NOT NULL, received_at INTEGER NOT NULL
            );
            CREATE TABLE IF NOT EXISTS threat_memory (
                fingerprint TEXT PRIMARY KEY, category TEXT NOT NULL, severity TEXT NOT NULL,
                evidence_json TEXT NOT NULL, first_seen INTEGER NOT NULL,
                last_seen INTEGER NOT NULL, occurrences INTEGER NOT NULL DEFAULT 1
            );
        """)
        self._db.commit()

    def __enter__(self) -> "Nexus":
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        self.close()

    def close(self) -> None:
        self._db.close()

    def register_repository(self, repo_id: str, *, default_branch: str = "main",
                            metadata: dict | None = None, now: int | None = None) -> None:
        if not repo_id or len(repo_id) > 256:
            raise ValueError("repo_id must be 1..256 characters")
        if not default_branch or len(default_branch) > 128:
            raise ValueError("default_branch must be 1..128 characters")
        encoded = json.dumps(metadata or {}, sort_keys=True, separators=(",", ":"))
        timestamp = int(time.time()) if now is None else now
        self._db.execute("""
            INSERT INTO repositories(repo_id, default_branch, metadata_json, registered_at)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(repo_id) DO UPDATE SET
              default_branch=excluded.default_branch, metadata_json=excluded.metadata_json
        """, (repo_id, default_branch, encoded, timestamp))
        self._db.commit()

    def repositories(self) -> list[dict]:
        rows = self._db.execute("SELECT * FROM repositories ORDER BY repo_id").fetchall()
        return [{"repo_id": r["repo_id"], "default_branch": r["default_branch"],
                 "metadata": json.loads(r["metadata_json"]), "registered_at": r["registered_at"]}
                for r in rows]

    def ingest(self, envelope: MeshEnvelope, *, node_secrets: Mapping[str, bytes],
               now: int | None = None) -> bool:
        verify_envelope(envelope, node_secrets=node_secrets, now=now)
        encoded = json.dumps(envelope.payload, sort_keys=True, separators=(",", ":"))
        try:
            self._db.execute("""
                INSERT INTO events(event_id, origin, kind, digest, payload_json, received_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (envelope.event_id, envelope.origin, envelope.kind, envelope.digest(),
                  encoded, int(time.time()) if now is None else now))
            self._db.commit()
            return True
        except sqlite3.IntegrityError:
            self._db.rollback()
            row = self._db.execute("SELECT digest FROM events WHERE event_id=?",
                                   (envelope.event_id,)).fetchone()
            if row and row["digest"] == envelope.digest():
                return False
            raise MeshError("event ID collision with different content")

    def remember_threat(self, *, fingerprint: str, category: str, severity: str,
                        evidence: dict, now: int | None = None) -> None:
        if len(fingerprint) != 64 or any(c not in "0123456789abcdef" for c in fingerprint):
            raise ValueError("fingerprint must be a lowercase SHA-256 digest")
        if not category or not severity:
            raise ValueError("category and severity are required")
        timestamp = int(time.time()) if now is None else now
        encoded = json.dumps(evidence, sort_keys=True, separators=(",", ":"))
        self._db.execute("""
            INSERT INTO threat_memory(fingerprint, category, severity, evidence_json,
                                      first_seen, last_seen, occurrences)
            VALUES (?, ?, ?, ?, ?, ?, 1)
            ON CONFLICT(fingerprint) DO UPDATE SET
              last_seen=excluded.last_seen, occurrences=threat_memory.occurrences+1,
              evidence_json=excluded.evidence_json
        """, (fingerprint, category, severity, encoded, timestamp, timestamp))
        self._db.commit()

    def find_threat(self, fingerprint: str) -> dict | None:
        row = self._db.execute("SELECT * FROM threat_memory WHERE fingerprint=?",
                               (fingerprint,)).fetchone()
        if row is None:
            return None
        return {"fingerprint": row["fingerprint"], "category": row["category"],
                "severity": row["severity"], "evidence": json.loads(row["evidence_json"]),
                "first_seen": row["first_seen"], "last_seen": row["last_seen"],
                "occurrences": row["occurrences"]}
