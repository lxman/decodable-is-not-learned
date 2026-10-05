# Test-only dependency slice; origin in LOCAL-TEST-MAP.json.
import unittest
import tempfile
import os
from pathlib import Path

class Inventory(unittest.TestCase):

    def test_contract(self):
        from exp7integration.inventory import enumerate_tree, verify_classification, ReadOnlyCampaign
        from exp7stats.common import dumps, Refusal
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = root / 'receipt.json'
            path.write_bytes(dumps({'stage': 'predictor-preflight'}))
            verify_classification(root, {'path': path.name, 'phase': 'predictor'})
            self.assertEqual(set(enumerate_tree(root)[0]), {path.name})
            path.write_bytes(dumps({'stage': 'outcome-preflight'}))
            with self.assertRaises(Refusal):
                verify_classification(root, {'path': path.name, 'phase': 'predictor'})
            guard = ReadOnlyCampaign(root)
            guard.start()
            try:
                fleeting = root / 'probe'
                fleeting.write_bytes(b'x')
                fleeting.unlink()
                with self.assertRaises(Refusal):
                    guard.check()
            finally:
                guard.stop()

    def _inventory_fixture(self, tmp):
        from exp7stats.common import CONTACT_ROOTS, SCHEMA, dumps
        root, repo = Path(tmp) / 'campaign', Path(tmp) / 'repository'
        (root / 'statistics/power').mkdir(parents=True)
        repo.mkdir()
        (root / 'statistics/power/CLAIM.json').write_bytes(dumps(
            {'schema': SCHEMA, 'stage': 'power', 'production': False}))
        specification = {'covered_roots': list(CONTACT_ROOTS),
            'repository_roots': list(CONTACT_ROOTS) + ['receipts', 'preflight'],
            'entries': []}
        return root, repo, specification

    def test_clean_inventory_and_predictor_roots(self):
        from exp7integration.inventory import power_inventory
        from exp7stats.common import dumps, digest
        with tempfile.TemporaryDirectory() as tmp:
            root, repo, specification = self._inventory_fixture(tmp)
            inventory, snapshot = power_inventory(root, specification, production=False, repo=repo)
            self.assertEqual(set(snapshot[0]), {'statistics/power/CLAIM.json'})
            self.assertEqual([row['path'] for row in inventory['entries']], ['statistics/power/CLAIM.json'])
            specification['covered_roots'].append('units/predictor')
            specification['repository_roots'].append('units/predictor')
            for base in (root, repo):
                (base / 'units/predictor').mkdir(parents=True)
            (repo / 'preflight').mkdir()
            for base, name, prefix in ((root, 'probes/predictor.json', ''),
                                       (repo, 'receipts/predictor.json', 'repository/')):
                path = base / name
                path.parent.mkdir()
                body = dumps({'stage': 'predictor-preflight'})
                path.write_bytes(body)
                specification['entries'].append({'path': prefix + name, 'phase': 'predictor',
                                                 'kind': 'probe', 'sha256': digest(body)})
            inventory, snapshot = power_inventory(root, specification, production=False, repo=repo)
            self.assertEqual(set(snapshot[0]), {'statistics/power/CLAIM.json',
                                               'probes/predictor.json', 'repository/receipts/predictor.json'})
            self.assertEqual({row['path'] for row in inventory['entries']}, set(snapshot[0]))
            self.assertTrue({'units/predictor', 'repository/units/predictor',
                             'repository/preflight'} <= set(snapshot[1]))

    def test_empty_outcome_markers_refuse_at_both_roots(self):
        from exp7integration.inventory import power_inventory
        from exp7stats.common import Refusal
        for side in ('campaign', 'repository'):
            for name in ('units/outcome', 'units/endpoint', 'units/outcome-anchors'):
                with self.subTest(side=side, marker=name), tempfile.TemporaryDirectory() as tmp:
                    root, repo, specification = self._inventory_fixture(tmp)
                    power_inventory(root, specification, production=False, repo=repo)
                    marker = (root if side == 'campaign' else repo) / name
                    marker.mkdir(parents=True)
                    self.assertEqual(list(marker.iterdir()), [])
                    with self.assertRaisesRegex(Refusal, 'power requires absent outcome tree: ' + name):
                        power_inventory(root, specification, production=False, repo=repo)

    def test_outcome_marker_symlinks_refuse_at_both_roots(self):
        from exp7integration.inventory import power_inventory
        from exp7stats.common import Refusal
        for side in ('campaign', 'repository'):
            for name in ('units/outcome', 'units/endpoint', 'units/outcome-anchors'):
                with self.subTest(side=side, marker=name), tempfile.TemporaryDirectory() as tmp:
                    root, repo, specification = self._inventory_fixture(tmp)
                    power_inventory(root, specification, production=False, repo=repo)
                    marker = (root if side == 'campaign' else repo) / name
                    marker.parent.mkdir()
                    marker.symlink_to(Path(tmp) / 'absent')
                    self.assertFalse(marker.exists())
                    self.assertTrue(marker.is_symlink())
                    with self.assertRaises(Refusal):
                        power_inventory(root, specification, production=False, repo=repo)

    def test_transient_dir_fd_and_absolute_mutations_refuse(self):
        from exp7integration.inventory import power_inventory, ReadOnlyCampaign
        from exp7stats.common import Refusal
        for use_dir_fd in (False, True):
            with self.subTest(use_dir_fd=use_dir_fd), tempfile.TemporaryDirectory() as tmp:
                root, repo, specification = self._inventory_fixture(tmp)
                folder = root / 'probes'
                folder.mkdir()
                before = power_inventory(root, specification, production=False, repo=repo)
                directory_fd = os.open(folder, os.O_RDONLY)
                guard = ReadOnlyCampaign(root)
                guard.start()
                try:
                    path = folder / 'fleeting.json'
                    body = b'{"stage":"outcome-preflight"}\n'
                    if use_dir_fd:
                        descriptor = os.open('fleeting.json', os.O_WRONLY | os.O_CREAT | os.O_EXCL,
                                             0o600, dir_fd=directory_fd)
                        try:
                            self.assertEqual(os.write(descriptor, body), len(body))
                        finally:
                            os.close(descriptor)
                    else:
                        path.write_bytes(body)
                    self.assertTrue(path.is_file())
                    self.assertEqual(path.read_bytes(), body)
                    if use_dir_fd:
                        os.unlink('fleeting.json', dir_fd=directory_fd)
                    else:
                        path.unlink()
                    self.assertFalse(path.exists())
                    after = power_inventory(root, specification, production=False, repo=repo)
                    self.assertEqual(before, after, 'entry/exit inventory and snapshots must be identical')
                    with self.assertRaisesRegex(Refusal, 'transient campaign mutation during power'):
                        guard.check()
                    self.assertTrue({'open', 'os.remove'} <= {event for event, _ in guard.events})
                finally:
                    guard.stop()
                    os.close(directory_fd)

    def test_descriptor_mutations_refuse(self):
        from exp7integration.inventory import ReadOnlyCampaign
        from exp7stats.common import Refusal
        for operation in ('ftruncate', 'fdopen'):
            with self.subTest(operation=operation), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                path = root / 'buffer'
                path.write_bytes(b'old')
                descriptor = os.open(path, os.O_RDWR)
                guard = ReadOnlyCampaign(root)
                guard.start()
                try:
                    if operation == 'ftruncate':
                        os.ftruncate(descriptor, 0)
                        self.assertEqual(path.stat().st_size, 0)
                        expected_event = 'os.truncate'
                    else:
                        with os.fdopen(descriptor, 'wb', closefd=False) as stream:
                            stream.write(b'new-data')
                        self.assertEqual(path.read_bytes(), b'new-data')
                        expected_event = 'open'
                    with self.assertRaisesRegex(Refusal, 'transient campaign mutation during power'):
                        guard.check()
                    self.assertIn((expected_event, (str(descriptor),)), guard.events)
                finally:
                    guard.stop()
                    os.close(descriptor)

    def test_unattributed_relative_external_mutations_refuse(self):
        from exp7integration.inventory import ReadOnlyCampaign
        from exp7stats.common import Refusal
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / 'campaign'
            root.mkdir()
            external = Path(tmp) / 'outside'
            name = os.path.relpath(external)
            self.assertFalse(Path(name).is_absolute())
            guard = ReadOnlyCampaign(root)
            guard.start()
            try:
                Path(name).write_bytes(b'external-relative')
                self.assertEqual(external.read_bytes(), b'external-relative')
                Path(name).unlink()
                with self.assertRaisesRegex(Refusal, 'transient campaign mutation during power'):
                    guard.check()
            finally:
                guard.stop()

    def test_reads_absolute_external_writes_and_stop_remain_usable(self):
        from exp7integration.inventory import ReadOnlyCampaign
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / 'campaign'
            root.mkdir()
            path = root / 'input'
            path.write_bytes(b'read-only')
            external = Path(tmp) / 'outside'
            self.assertTrue(external.is_absolute())
            directory_fd = os.open(root, os.O_RDONLY)
            guard = ReadOnlyCampaign(root)
            guard.start()
            try:
                with open(os.path.relpath(path), 'rb') as stream:
                    self.assertEqual(stream.read(), b'read-only')
                descriptor = os.open('input', os.O_RDONLY, dir_fd=directory_fd)
                try:
                    with os.fdopen(descriptor, 'rb', closefd=False) as stream:
                        self.assertEqual(stream.read(), b'read-only')
                finally:
                    os.close(descriptor)
                external.write_bytes(b'external-absolute')
                self.assertEqual(external.read_bytes(), b'external-absolute')
                external.unlink()
                guard.check()
                self.assertEqual(guard.events, [])
                guard.stop()
                descriptor = os.open('inactive', os.O_WRONLY | os.O_CREAT | os.O_EXCL,
                                     0o600, dir_fd=directory_fd)
                try:
                    os.write(descriptor, b'inactive')
                    os.ftruncate(descriptor, 0)
                finally:
                    os.close(descriptor)
                os.unlink('inactive', dir_fd=directory_fd)
                guard.check()
                self.assertEqual(guard.events, [])
            finally:
                guard.stop()
                os.close(directory_fd)
