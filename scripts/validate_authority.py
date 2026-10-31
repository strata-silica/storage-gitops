#!/usr/bin/env python3
from pathlib import Path
import json

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

ruleset = json.loads((root / "governance/github/main-ruleset.json").read_text())
rule_types = {rule["type"] for rule in ruleset["rules"]}
assert {"deletion", "non_fast_forward", "required_signatures", "pull_request", "required_status_checks"} <= rule_types
status_rule = next(rule for rule in ruleset["rules"] if rule["type"] == "required_status_checks")
assert status_rule["parameters"]["required_status_checks"] == [{"context": "authority"}]

environments = yaml.safe_load((root / "governance/github/environments.yaml").read_text())["spec"]
assert environments["deploymentBranches"] == ["main"]
assert environments["secrets"] == []
assert len(environments["environments"]) == len(set(environments["environments"]))
print("GitHub governance declarations are valid")
