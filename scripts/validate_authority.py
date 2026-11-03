#!/usr/bin/env python3
from pathlib import Path
import json
import re
import sys

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

ceph = spec["domains"]["ceph"]
assert ceph["disposition"] == "cutover-approved"
assert ceph["releases"] == ["rook-ceph", "ceph-csi-drivers", "rook-ceph-cluster"]

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

release = (root / ".github/workflows/storage-static-release.yml").read_text()
assert "inputs.contract" in release and "inputs.execute" in release
assert "--server=https://kube-api.service.re8ch.com" in release
assert "ssh -M" not in release
for workflow_path in (root / ".github/workflows").glob("*.yml"):
    for job in yaml.safe_load(workflow_path.read_text())["jobs"].values():
        assert job.get("runs-on") == "ubuntu-24.04", workflow_path
assert "--retry-all-errors" in release and "--connect-timeout 10" in release
assert "jq -er '.value | strings | select(length > 0)'" in release
assert "operations/releases/ssa_executor.py" in release
assert "--server-side" not in release  # the bounded executor owns SSA arguments
assert "kubectl patch configmap" in release
result_upload = release.split("name: 'main-domain-release-result-${{ github.run_id }}'", 1)[0].rsplit(
    "- uses: actions/upload-artifact@", 1
)[1]
assert "continue-on-error: true" in result_upload
print("storage release workflow is bounded to reviewed contracts and durable state")

runtime_paths = set(re.findall(
    r"(?:operations/releases/[A-Za-z0-9_./-]+\.py|schemas/[A-Za-z0-9_.-]+\.json)",
    release + "\n" + "\n".join(path.read_text() for path in (root / "operations/releases").glob("*.py")),
))
missing = sorted(path for path in runtime_paths if not (root / path).is_file())
assert not missing, f"missing storage executor runtime files: {missing}"

release_modules = list((root / "operations/releases").glob("*.py"))
local_runtime_data = {
    path.with_name(filename)
    for path in release_modules
    for filename in re.findall(r'Path\(__file__\)\.with_name\(["\']([^"\']+)["\']\)', path.read_text())
}
missing_local_data = sorted(str(path.relative_to(root)) for path in local_runtime_data if not path.is_file())
assert not missing_local_data, f"missing storage executor local runtime data: {missing_local_data}"
for path in local_runtime_data:
    if path.suffix == ".json":
        json.loads(path.read_text())

sys.path.insert(0, str(root / "operations/releases"))
import ssa_executor  # noqa: F401,E402
print("storage SSA executor runtime imports are complete")

ceph_workflow = (root / ".github/workflows/ceph-static-release.yml").read_text()
compiler_workflow = (root / ".github/workflows/ceph-shadow-compile.yml").read_text()
assert ceph_workflow.count("KUBE_API_SERVER: https://kube-api.service.re8ch.com") == 2
assert "KUBE_API_SERVER: 'https://kube-api.service.re8ch.com'" in ceph_workflow
assert "KUBE_API_CA_PEM" not in ceph_workflow
assert "10.181.22.147:6443" not in ceph_workflow
assert (root / "operations/releases/ceph_cloud_request.py").is_file()
assert "strata-silica/storage-gitops" in (root / "operations/releases/ceph_cloud_request.py").read_text()
for legacy in (
    "https://github.com/re8ch/service-backend/.github/workflows/ceph-shadow-compile.yml",
    "oci://ghcr.io/re8ch/service-backend-release/",
):
    assert legacy not in ceph_workflow + compiler_workflow
assert "strata-silica/storage-gitops" in compiler_workflow

runtime_profile = json.loads((root / "operations/releases/ceph-runtime-profile.json").read_text())
static_releases = {
    document["metadata"]["name"]: document["spec"]["contractDigest"]
    for document in yaml.safe_load_all(
        (root / "clusters/re8ch/components/release-compat/ceph-static-releases.yaml").read_text()
    )
}
assert runtime_profile["contracts"] == static_releases
assert runtime_profile["execution"]["repository"] == "strata-silica/storage-gitops"
print("Ceph compiler and split executor identities are bound to storage-gitops")
