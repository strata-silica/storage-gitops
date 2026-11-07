from pathlib import Path
import subprocess
import sys
import unittest
from unittest import mock

sys.path.insert(0, str(Path(__file__).parent))
import ceph_health


class CephHealthTest(unittest.TestCase):
    cluster = {"status": {"phase": "Ready", "conditions": [{"type": "Ready", "status": "True"}],
                          "ceph": {"health": "HEALTH_WARN", "versions": {"mon": {"v": 1}, "osd": {"v": 1}, "mds": {"v": 1}}}}}
    filesystem = {"status": {"phase": "Ready"}}
    pool = {"status": {"phase": "Ready"}}

    def test_observation_retries_transient_exec_failure(self) -> None:
        failure = subprocess.CalledProcessError(1, ["kubectl"])
        with mock.patch.object(ceph_health, "command", side_effect=[failure, self.cluster, self.filesystem, self.pool]), \
                mock.patch.object(ceph_health.time, "monotonic", side_effect=[0, 1]), \
                mock.patch.object(ceph_health.time, "sleep") as sleep:
            cluster, filesystem, pool = ceph_health.converged_ceph_status(timeout_seconds=30, interval_seconds=1)
        self.assertEqual((cluster, filesystem, pool), (self.cluster, self.filesystem, self.pool))
        sleep.assert_called_once_with(1)

    def test_observation_times_out_without_ready_filesystem(self) -> None:
        filesystem = {"status": {"phase": "Progressing"}}
        with mock.patch.object(ceph_health, "command", side_effect=[self.cluster, filesystem, self.pool]), \
                mock.patch.object(ceph_health.time, "monotonic", side_effect=[0, 2]), \
                mock.patch.object(ceph_health.time, "sleep"):
            with self.assertRaisesRegex(SystemExit, "did not converge"):
                ceph_health.converged_ceph_status(timeout_seconds=1, interval_seconds=1)


if __name__ == "__main__":
    unittest.main()
