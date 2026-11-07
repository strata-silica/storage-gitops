#!/usr/bin/env python3
"""Fail-closed Ceph acceptance using status plus non-destructive smoke state."""
from __future__ import annotations

import argparse
import json
import subprocess
import time


def command(*argv: str) -> dict:
    completed = subprocess.run(argv, check=True, text=True, capture_output=True, timeout=120)
    return json.loads(completed.stdout)


def require(value: bool, message: str) -> None:
    if not value:
        raise SystemExit(message)


def daemon_count(cluster: dict, daemon: str) -> int:
    versions = cluster.get("status", {}).get("ceph", {}).get("versions", {}).get(daemon, {})
    return sum(versions.values())


def converged_ceph_status(timeout_seconds: int = 300, interval_seconds: int = 10) -> tuple[dict, dict, dict]:
    deadline = time.monotonic() + timeout_seconds
    while True:
        try:
            cluster = command("kubectl", "get", "cephcluster", "rook-ceph", "-n", "rook-ceph", "-o", "json")
            filesystem = command("kubectl", "get", "cephfilesystem", "re8ch-files", "-n", "rook-ceph", "-o", "json")
            pool = command("kubectl", "get", "cephblockpool", "r640-rbd", "-n", "rook-ceph", "-o", "json")
            status = cluster.get("status", {})
            ceph = status.get("ceph", {})
            ready = (
                status.get("phase") == "Ready"
                and any(item.get("type") == "Ready" and item.get("status") == "True" for item in status.get("conditions", []))
                and ceph.get("health") in {"HEALTH_OK", "HEALTH_WARN"}
                and daemon_count(cluster, "mon") >= 1
                and daemon_count(cluster, "osd") >= 1
                and filesystem.get("status", {}).get("phase") == "Ready"
                and filesystem.get("status", {}).get("activeMDS", 0) >= 1
                and pool.get("status", {}).get("phase") == "Ready"
            )
            if ready:
                return cluster, filesystem, pool
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired, json.JSONDecodeError):
            pass
        if time.monotonic() >= deadline:
            raise SystemExit("Ceph status did not converge before the observation timeout")
        time.sleep(interval_seconds)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--release", required=True, choices=["rook-ceph", "ceph-csi-drivers", "rook-ceph-cluster"])
    args = parser.parse_args()
    evidence: dict[str, object] = {"release": args.release}
    deployments = command("kubectl", "get", "deployment", "-n", "rook-ceph", "-o", "json")["items"]
    required = {"rook-ceph-operator", "ceph-csi-controller-manager", "rook-ceph.rbd.csi.ceph.com-ctrlplugin", "rook-ceph.cephfs.csi.ceph.com-ctrlplugin"}
    by_name = {item["metadata"]["name"]: item for item in deployments}
    for name in required:
        item = by_name.get(name)
        require(item is not None, f"missing deployment {name}")
        require(item.get("status", {}).get("readyReplicas", 0) >= item.get("spec", {}).get("replicas", 1), f"deployment not ready: {name}")
    daemonsets = command("kubectl", "get", "daemonset", "-n", "rook-ceph", "-o", "json")["items"]
    node_plugins = [item for item in daemonsets if item["metadata"]["name"] in {"rook-ceph.rbd.csi.ceph.com-nodeplugin", "rook-ceph.cephfs.csi.ceph.com-nodeplugin"}]
    require(len(node_plugins) == 2, "both CSI node plugins are required")
    for item in node_plugins:
        status = item.get("status", {})
        require(status.get("numberReady", 0) == status.get("desiredNumberScheduled", -1), f'node plugin not ready: {item["metadata"]["name"]}')
    cluster, filesystem, pool = converged_ceph_status()
    for smoke_name in ("rbd-smoke", "cephfs-smoke"):
        pvc = command("kubectl", "get", "persistentvolumeclaim", smoke_name, "-n", "ceph-storage-smoke", "-o", "json")
        smoke = command("kubectl", "get", "deployment", smoke_name, "-n", "ceph-storage-smoke", "-o", "json")
        require(pvc.get("status", {}).get("phase") == "Bound", f"{smoke_name} PVC is not Bound")
        require(smoke.get("status", {}).get("readyReplicas", 0) >= 1, f"{smoke_name} read/write smoke is not ready")
    evidence.update({"cephHealth": cluster["status"]["ceph"]["health"],
                     "monDaemons": daemon_count(cluster, "mon"), "osdDaemons": daemon_count(cluster, "osd"),
                     "filesystem": filesystem["status"]["phase"], "blockPool": pool["status"]["phase"],
                     "csiNodePlugins": len(node_plugins), "rbdSmoke": "ready", "cephfsSmoke": "ready"})
    print(json.dumps(evidence, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
