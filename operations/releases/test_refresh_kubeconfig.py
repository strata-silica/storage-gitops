import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

import yaml

sys.path.insert(0, str(Path(__file__).parent))
import refresh_kubeconfig
from ssa_executor import Rejected


class RefreshKubeconfigTest(unittest.TestCase):
    oidc = {
        'ACTIONS_ID_TOKEN_REQUEST_URL': 'https://example.actions.githubusercontent.com/token',
        'ACTIONS_ID_TOKEN_REQUEST_TOKEN': 'request-token',
        'EXECUTOR_AUDIENCE': 'https://kube-api.re8ch.com/release-executor-data-storage',
    }

    def kubeconfig(self, directory: str, token: str = 'initial-token') -> Path:
        path = Path(directory) / 'executor.kubeconfig'
        path.write_text(yaml.safe_dump({
            'users': [{'name': 'release-executor', 'user': {'token': token}}],
        }))
        return path

    def test_fresh_initial_credential_is_reused(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = self.kubeconfig(directory)
            env = {**self.oidc, 'KUBECONFIG': str(path)}
            with mock.patch.dict(os.environ, env, clear=True), \
                    mock.patch.object(refresh_kubeconfig.Executor, 'actions_kube_token', return_value=None):
                refresh_kubeconfig.refresh()
            self.assertEqual(yaml.safe_load(path.read_text())['users'][0]['user']['token'], 'initial-token')

    def test_refreshed_credential_replaces_initial_credential(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = self.kubeconfig(directory)
            env = {**self.oidc, 'KUBECONFIG': str(path)}
            with mock.patch.dict(os.environ, env, clear=True), \
                    mock.patch.object(refresh_kubeconfig.Executor, 'actions_kube_token', return_value='new-token'):
                refresh_kubeconfig.refresh()
            self.assertEqual(yaml.safe_load(path.read_text())['users'][0]['user']['token'], 'new-token')

    def test_reuse_requires_complete_oidc_context(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = self.kubeconfig(directory)
            with mock.patch.dict(os.environ, {'KUBECONFIG': str(path)}, clear=True):
                with self.assertRaisesRegex(Rejected, 'incomplete Actions OIDC'):
                    refresh_kubeconfig.refresh()


if __name__ == '__main__':
    unittest.main()
