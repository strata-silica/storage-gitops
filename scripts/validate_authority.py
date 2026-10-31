#!/usr/bin/env python3
from pathlib import Path

import yaml


root = Path(__file__).resolve().parents[1]
authority = yaml.safe_load((root / "governance/authority.yaml").read_text())
spec = authority["spec"]

assert spec["phase"] in {"inventory", "shadow", "cutover-approved", "active"}
assert spec["destinationRepository"] == "strata-silica/storage-gitops"
if spec["phase"] in {"inventory", "shadow"}:
    assert spec["currentExecutionRepository"] == "re8ch/service-backend"
    assert spec["clusterMutationEnabled"] is False

releases = spec["domains"]["data-storage"]["releases"]
assert len(releases) == len(set(releases))
assert "main-data-storage-supabase-pg-re8ch" not in releases
print("storage authority declaration is valid")
