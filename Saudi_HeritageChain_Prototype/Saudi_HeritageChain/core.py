import hashlib
import json
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path

DB = Path(__file__).parent / 'data' / 'heritage.db'

def connect():
    DB.parent.mkdir(exist_ok=True)
    db = sqlite3.connect(DB)
    db.row_factory = sqlite3.Row
    db.execute('CREATE TABLE IF NOT EXISTS artifacts (id TEXT PRIMARY KEY, payload TEXT NOT NULL)')
    db.execute('CREATE TABLE IF NOT EXISTS ledger (seq INTEGER PRIMARY KEY, artifact TEXT, time TEXT, kind TEXT, payload TEXT, previous TEXT, hash TEXT)')
    db.execute('CREATE TABLE IF NOT EXISTS blocks (height INTEGER PRIMARY KEY, event_seq INTEGER UNIQUE, time TEXT, event_hash TEXT, previous TEXT, nonce INTEGER, hash TEXT)')
    return db

def digest(value):
    return hashlib.sha256(value.encode()).hexdigest()

def append(db, aid, kind, data):
    db.execute('UPDATE artifacts SET payload=payload WHERE id=?', (aid,))
    valid, reason = verify_blocks(db)
    if not valid:
        raise ValueError('Blockchain check failed; writes blocked: ' + reason)
    last = db.execute('SELECT hash FROM ledger ORDER BY seq DESC LIMIT 1').fetchone()
    prev = last['hash'] if last else '0' * 64
    time = datetime.now(timezone.utc).isoformat()
    payload = json.dumps(data, sort_keys=True, ensure_ascii=False)
    hashed = digest(json.dumps([aid, time, kind, payload, prev], ensure_ascii=False))
    db.execute('INSERT INTO ledger (artifact,time,kind,payload,previous,hash) VALUES (?,?,?,?,?,?)', (aid,time,kind,payload,prev,hashed))
    event_seq = db.execute('SELECT last_insert_rowid()').fetchone()[0]
    mine_block(db, event_seq, hashed)

def register(name, category, owner, location, tag, image_hash=''):
    if not all(str(x).strip() for x in [name, owner, location, tag]):
        raise ValueError('Name, custodian, location and tag are required.')
    aid = 'SA-HC-' + uuid.uuid4().hex[:10].upper()
    data = dict(id=aid, name=name.strip(), category=category, owner=owner.strip(), location=location.strip(), tag=tag.strip(), image_hash=image_hash, condition='Good')
    with connect() as db:
        for row in db.execute('SELECT payload FROM artifacts'):
            if json.loads(row['payload'])['tag'] == tag.strip():
                raise ValueError('This fingerprint/tag is already registered.')
        db.execute('INSERT INTO artifacts VALUES (?,?)', (aid,json.dumps(data,ensure_ascii=False)))
        append(db, aid, 'Registration', data)
    return aid

def artifacts():
    with connect() as db:
        return [json.loads(r['payload']) for r in db.execute('SELECT payload FROM artifacts ORDER BY rowid')]

def events(aid=None):
    with connect() as db:
        rows = db.execute('SELECT * FROM ledger WHERE artifact=? ORDER BY seq', (aid,)) if aid else db.execute('SELECT * FROM ledger ORDER BY seq')
        return [dict(r) for r in rows]

def record(aid, kind, details):
    with connect() as db:
        row = db.execute('SELECT payload FROM artifacts WHERE id=?', (aid,)).fetchone()
        if not row:
            raise ValueError('Artifact not found.')
        data = json.loads(row['payload'])
        if kind == 'Movement': data['location'] = details['destination']
        if kind == 'Custody transfer': data['owner'] = details['custodian']
        if kind == 'Conservation': data['condition'] = details['condition']
        db.execute('UPDATE artifacts SET payload=? WHERE id=?', (json.dumps(data,ensure_ascii=False),aid))
        append(db, aid, kind, details)

def verify():
    previous = '0' * 64
    snapshots = {}
    for row in events():
        expected = digest(json.dumps([row['artifact'],row['time'],row['kind'],row['payload'],previous],ensure_ascii=False))
        if row['previous'] != previous or row['hash'] != expected:
            return False, 'Ledger mismatch at event ' + str(row['seq'])
        previous = row['hash']
        detail = json.loads(row['payload'])
        if row['kind'] == 'Registration': snapshots[row['artifact']] = detail
        elif row['artifact'] in snapshots:
            if row['kind'] == 'Movement': snapshots[row['artifact']]['location'] = detail['destination']
            if row['kind'] == 'Custody transfer': snapshots[row['artifact']]['owner'] = detail['custodian']
            if row['kind'] == 'Conservation': snapshots[row['artifact']]['condition'] = detail['condition']
    if {a['id']:a for a in artifacts()} != snapshots:
        return False, 'Artifact records do not match the ledger.'
    return True, 'All stored events and artifact records match.'

def assess(artifact, tag, temperature, humidity, permit, route, image_hash=''):
    findings = []
    score = 0
    if tag.strip() != artifact['tag']:
        score += 45; findings.append('Fingerprint/tag mismatch: manual authentication needed.')
    if image_hash and artifact['image_hash'] and image_hash != artifact['image_hash']:
        score += 20; findings.append('Photo bytes differ from registered file. This does not establish forgery.')
    if not permit:
        score += 30; findings.append('Movement permit not confirmed.')
    if route:
        score += 20; findings.append('Unexpected route reported.')
    if temperature > 30 or temperature < 10:
        score += 10; findings.append('Temperature outside demo conservation range (10–30 °C).')
    if humidity > 65 or humidity < 30:
        score += 10; findings.append('Humidity outside demo conservation range (30–65%).')
    return dict(score=min(score,100), level='High' if score >= 50 else 'Medium' if score >= 20 else 'Low', findings=findings or ['No demo rule triggered. Physical authenticity remains unverified.'])

def seed():
    if not artifacts():
        register('Demo Nabataean pottery', 'Pottery', 'Demo Heritage Museum', 'Riyadh', 'DEMO-NFC-001')
        register('Demo historical manuscript', 'Manuscript', 'Demo National Archive', 'Jeddah', 'DEMO-NANO-002')


DIFFICULTY = 2  # Small demonstration proof of work, not production security.

def block_hash(height, event_seq, time, event_hash, previous, nonce):
    return digest(json.dumps([height, event_seq, time, event_hash, previous, nonce]))

def mine_block(db, event_seq, event_hash):
    last = db.execute('SELECT height,hash FROM blocks ORDER BY height DESC LIMIT 1').fetchone()
    height = last['height'] + 1 if last else 0
    previous = last['hash'] if last else '0' * 64
    time = datetime.now(timezone.utc).isoformat()
    nonce = 0
    hashed = block_hash(height,event_seq,time,event_hash,previous,nonce)
    while not hashed.startswith('0' * DIFFICULTY):
        nonce += 1
        hashed = block_hash(height,event_seq,time,event_hash,previous,nonce)
    db.execute('INSERT INTO blocks VALUES (?,?,?,?,?,?,?)', (height,event_seq,time,event_hash,previous,nonce,hashed))

def blocks():
    with connect() as db:
        return [dict(r) for r in db.execute('SELECT * FROM blocks ORDER BY height')]

def verify_blocks(db=None):
    if db is None:
        with connect() as connection:
            return verify_blocks(connection)
    chain = list(db.execute('SELECT * FROM blocks ORDER BY height'))
    ledger = list(db.execute('SELECT * FROM ledger ORDER BY seq'))
    if len(chain) != len(ledger):
        return False, 'Event and block counts differ. Legacy data needs explicit migration.'
    previous = '0' * 64
    event_previous = '0' * 64
    for height, (block,event) in enumerate(zip(chain,ledger)):
        expected = block_hash(block['height'],block['event_seq'],block['time'],block['event_hash'],block['previous'],block['nonce'])
        event_expected = digest(json.dumps([event['artifact'],event['time'],event['kind'],event['payload'],event_previous],ensure_ascii=False))
        if (block['height'] != height or block['previous'] != previous or block['hash'] != expected
            or not expected.startswith('0' * DIFFICULTY) or block['event_seq'] != event['seq']
            or block['event_hash'] != event['hash'] or event['hash'] != event_expected or event['previous'] != event_previous):
            return False, 'Tampering or invalid proof of work at block ' + str(height)
        previous = block['hash']
        event_previous = event['hash']
    return True, 'Block links, proof of work and event commitments are valid.'

def migrate_legacy():
    valid, message = verify()
    if not valid:
        raise ValueError(message)
    with connect() as db:
        db.execute('UPDATE artifacts SET payload=payload')
        if db.execute('SELECT COUNT(*) FROM blocks').fetchone()[0]:
            raise ValueError('Blocks already exist; automatic repair is forbidden.')
        for row in db.execute('SELECT seq,hash FROM ledger ORDER BY seq').fetchall():
            mine_block(db,row['seq'],row['hash'])

def checkpoint():
    chain = blocks()
    return dict(type='heritagechain-checkpoint-v1', height=chain[-1]['height'] if chain else -1,
                hash=chain[-1]['hash'] if chain else '0' * 64)

def check_checkpoint(saved):
    if not isinstance(saved,dict) or saved.get('type') != 'heritagechain-checkpoint-v1':
        return False, 'Invalid checkpoint format.'
    height = saved.get('height')
    if not isinstance(height,int) or height < -1 or not isinstance(saved.get('hash'),str):
        return False, 'Invalid checkpoint fields.'
    valid, reason = verify_blocks()
    if not valid: return False, reason
    chain = blocks()
    actual = '0' * 64 if height == -1 else chain[height]['hash'] if height < len(chain) else None
    if actual != saved['hash']:
        return False, 'Checkpoint mismatch: chain was rewritten or shortened.'
    return True, 'Previously saved checkpoint matches. Later blocks may have been added.'
