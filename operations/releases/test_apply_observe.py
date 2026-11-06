import datetime as dt
import json
import subprocess
import sys
import uuid
import unittest
import tempfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import ssa_executor as executor
from unified_bundle import canonical, compile_bundle, digest
NOW = dt.datetime(2026, 10, 23, tzinfo=dt.timezone.utc)

def contract(inventory=None, deletion=None):
    inventory = inventory or ["apps/Deployment/demo/demo"]
    return {
        "apiVersion": "delivery.re8ch.com/v1alpha1", "kind": "ReleaseContract",
        "metadata": {"name": "demo"},
        "spec": {
            "target": {"cluster": "re8ch", "namespace": "demo"},
            "source": {"renderer": "kustomize", "revision": "a" * 40},
            "provenance": {
                "repository": "re8ch/delivery-products-gitops", "workflow": ".github/workflows/static-release.yml",
                "ref": "refs/heads/main", "environment": "production",
                "audience": "https://kube-api.re8ch.com/release-executor",
                "signer": "https://github.com/re8ch/delivery-products-gitops/.github/workflows/static-release.yml@refs/heads/main",
                "issuer": "https://token.actions.githubusercontent.com",
            },
            "authorization": {"fieldManager": "re8ch-release/demo", "resources": ["apps/Deployment"], "objectNames": ["demo"]},
            "inventory": {"digest": digest(canonical(inventory))},
            "lifecycle": {"prune": True, "healthTimeoutSeconds": 1, "protectedKinds": [], "deletionAllowlist": deletion or []},
        },
    }

def rendered(name="demo"):
    return f"""apiVersion: apps/v1
kind: Deployment
metadata: {{name: {name}, namespace: demo}}
spec:
  replicas: 1
  template:
    spec:
      containers:
      - {{name: demo, image: 'registry.example/demo@sha256:{'a' * 64}'}}
""".encode()

def prepare(tmp_path, sequence=1, operation_id=None, previous=None):
    value = contract()
    archive, manifest = compile_bundle(value, rendered())
    bundle_path = tmp_path / "bundle.tar.gz"
    bundle_path.write_bytes(archive)
    operation = {
        "apiVersion": "delivery.re8ch.com/release-operation/v1alpha1",
        "operationId": operation_id or str(uuid.uuid4()), "sequence": sequence,
        "action": "reconcile", "idempotencyKey": "0123456789abcdef",
        "releaseId": "demo", "target": "re8ch/demo", "contractDigest": digest(canonical(value)),
        "bundle": {"reference": "oci://registry.example/releases/demo", "digest": digest(archive),
                   "payloadDigest": digest(archive),
                   "signer": "https://github.com/re8ch/delivery-products-gitops/.github/workflows/static-release.yml@refs/heads/main",
                   "issuer": "https://token.actions.githubusercontent.com"},
        "inventoryDigest": manifest["inventoryDigest"],
        "github": {"repository": "re8ch/delivery-products-gitops", "workflow": ".github/workflows/static-release.yml",
                   "ref": "refs/heads/main", "commit": "b" * 40, "runId": "123", "environment": "production",
                   "audience": "https://kube-api.re8ch.com/release-executor"},
        "issuedAt": (NOW - dt.timedelta(minutes=1)).isoformat(),
        "expiresAt": (NOW + dt.timedelta(minutes=10)).isoformat(), "nonce": "0123456789abcdef",
    }
    if previous:
        operation["previousApprovedDigest"] = previous
    return value, operation, bundle_path

class Runner:
    def __init__(self, conflict=False, live=None, pulled_bundle=None):
        self.calls = []
        self.conflict = conflict
        self.live = live
        self.pulled_bundle = pulled_bundle

    def __call__(self, argv, **kwargs):
        self.calls.append((argv, kwargs.get("input")))
        if self.conflict and "--dry-run=server" in argv and "--force-conflicts" not in argv:
            return subprocess.CompletedProcess(argv, 1, "", "field manager conflict")
        if argv[:2] == ["kubectl", "get"]:
            body = self.live or {"metadata": {"generation": 2}, "spec": {"replicas": 1},
                                 "status": {"observedGeneration": 2, "availableReplicas": 1}}
            return subprocess.CompletedProcess(argv, 0, json.dumps(body), "")
        if argv[:3] == ["flux", "pull", "artifact"] and self.pulled_bundle:
            Path(argv[argv.index("--output") + 1], "release.bundle").write_bytes(self.pulled_bundle)
        return subprocess.CompletedProcess(argv, 0, "ok", "")
class ApplyObserveTest(unittest.TestCase):
    def test_apply_records_acceptance_without_claiming_health(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            value, operation, path = prepare(root)
            ex = executor.Executor(runner=Runner(), now=lambda: NOW)
            ex.apply_only = True
            def reject_health(*args):
                raise AssertionError('SSA must not call runtime health')
            ex.wait_healthy = reject_health
            result = ex.reconcile(value, operation, path, root/'state', verify_signature=False)
            self.assertEqual(result['outcome'], 'applied')
            self.assertEqual(result['health']['status'], 'unknown')
            state = executor.Store(root/'state', operation['releaseId']).state()
            self.assertEqual(state['acceptedDigest'], operation['bundle']['digest'])
            self.assertNotIn('healthyDigest', state)

    def test_ssa_conflict_still_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            value, operation, path = prepare(root)
            ex = executor.Executor(runner=Runner(conflict=True), now=lambda: NOW)
            ex.apply_only = True
            with self.assertRaises(executor.Rejected):
                ex.reconcile(value, operation, path, root/'state', verify_signature=False)
