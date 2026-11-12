#!/usr/bin/env python3
"""Validate the NEURO-CORE capability register without claiming implementation."""
import json
from pathlib import Path

path = Path(__file__).resolve().parents[1] / "neuro-core" / "manifest.json"
data = json.loads(path.read_text(encoding="utf-8"))
assert data["architecture"] == "NEURO-CORE"
assert data["target_innovations_per_repository"] == 666
clusters = data["clusters"]
assert len(clusters) == 9, f"expected 9 clusters, got {len(clusters)}"
ids = []
for cluster in clusters:
    assert cluster["capacity"] == 74
    assert len(cluster["items"]) == 74
    for item in cluster["items"]:
        assert item["status"] in {"PROPOSED", "BACKLOG", "IMPLEMENTED", "TESTED", "VERIFIED", "INTEGRATED", "RELEASED"}
        ids.append(item["id"])
assert len(ids) == 666, f"expected 666 IDs, got {len(ids)}"
assert len(set(ids)) == 666, "duplicate capability IDs"
print(f"NEURO-CORE register valid: {len(clusters)} clusters, {len(ids)} unique slots")
