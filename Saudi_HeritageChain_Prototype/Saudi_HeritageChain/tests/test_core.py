import json
import tempfile
import unittest
from pathlib import Path
import core

class TestHeritage(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.old=core.DB
        core.DB=Path(self.temp.name)/'data'/'test.db'
        self.aid=core.register('Test','Coin','Museum','Riyadh','TAG1')
    def tearDown(self):
        core.DB=self.old
        self.temp.cleanup()
    def test_updates_and_audit(self):
        core.record(self.aid,'Movement',{'destination':'Jeddah'})
        core.record(self.aid,'Custody transfer',{'custodian':'Archive'})
        self.assertEqual(core.artifacts()[0]['location'],'Jeddah')
        self.assertEqual(core.artifacts()[0]['owner'],'Archive')
        self.assertTrue(core.verify()[0])
    def test_duplicate(self):
        with self.assertRaises(ValueError): core.register('Other','Coin','Museum','Riyadh','TAG1')
    def test_tamper(self):
        with core.connect() as db: db.execute("UPDATE ledger SET payload='{}' WHERE seq=1")
        self.assertFalse(core.verify()[0])
    def test_registry_tamper(self):
        data=core.artifacts()[0]; data['owner']='Changed'
        with core.connect() as db: db.execute('UPDATE artifacts SET payload=?',(json.dumps(data),))
        self.assertFalse(core.verify()[0])
    def test_alerts(self):
        result=core.assess(core.artifacts()[0],'WRONG',35,80,False,True)
        self.assertEqual(result['level'],'High')
        self.assertEqual(result['score'],100)
        self.assertEqual(core.assess(core.artifacts()[0],'TAG1',22,45,True,False)['score'],0)
    def test_block_protection(self):
        self.assertTrue(core.verify_blocks()[0])
        saved=core.checkpoint()
        core.record(self.aid,'Movement',{'destination':'Jeddah'})
        self.assertTrue(core.check_checkpoint(saved)[0])
        with core.connect() as db: db.execute('UPDATE blocks SET nonce=nonce+1 WHERE height=0')
        self.assertFalse(core.verify_blocks()[0])
        with self.assertRaises(ValueError): core.record(self.aid,'Movement',{'destination':'X'})
        self.assertEqual(core.artifacts()[0]['location'],'Jeddah')
    def test_checkpoint_detects_truncation(self):
        core.record(self.aid,'Exhibition',{'notes':'Test'})
        saved=core.checkpoint()
        with core.connect() as db:
            db.execute('DELETE FROM blocks WHERE height=1')
            db.execute('DELETE FROM ledger WHERE seq=2')
        self.assertTrue(core.verify_blocks()[0])
        self.assertFalse(core.check_checkpoint(saved)[0])
    def test_legacy_migration(self):
        with core.connect() as db: db.execute('DELETE FROM blocks')
        self.assertFalse(core.verify_blocks()[0])
        core.migrate_legacy()
        self.assertTrue(core.verify_blocks()[0])
