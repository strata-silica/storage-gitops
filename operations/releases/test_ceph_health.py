from pathlib import Path
import subprocess
import sys
import unittest
from unittest import mock

sys.path.insert(0, str(Path(__file__).parent))
import ceph_health


class CephHealthTest(unittest.TestCase):
    ready = {
        "monmap": {"num_mons": 1},
        "quorum": [0],
        "osdmap": {"num_osds": 1, "num_up_osds": 1, "num_in_osds": 1},
        "pgmap": {"num_pgs": 2, "pgs_by_state": [{"state_name": "active+clean", "count": 2}]},
    }

    def test_observation_retries_transient_exec_failure(self) -> None:
        failure = subprocess.CalledProcessError(1, ["kubectl"])
        with mock.patch.object(ceph_health, "command", side_effect=[failure, self.ready]), \
                mock.patch.object(ceph_health.time, "monotonic", side_effect=[0, 1]), \
                mock.patch.object(ceph_health.time, "sleep") as sleep:
            status, clean = ceph_health.converged_ceph_status(timeout_seconds=30, interval_seconds=1)
        self.assertEqual(status, self.ready)
        self.assertEqual(clean, 2)
        sleep.assert_called_once_with(1)

    def test_observation_times_out_without_healthy_pgs(self) -> None:
        recovering = {**self.ready, "pgmap": {"num_pgs": 2, "pgs_by_state": [{"state_name": "active+recovering", "count": 2}]}}
        with mock.patch.object(ceph_health, "command", return_value=recovering), \
                mock.patch.object(ceph_health.time, "monotonic", side_effect=[0, 2]), \
                mock.patch.object(ceph_health.time, "sleep"):
            with self.assertRaisesRegex(SystemExit, "did not converge"):
                ceph_health.converged_ceph_status(timeout_seconds=1, interval_seconds=1)


if __name__ == "__main__":
    unittest.main()
