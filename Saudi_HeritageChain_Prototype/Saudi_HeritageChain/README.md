# Saudi HeritageChain — Python / Streamlit prototype
Based on the supplied Saudi HeritageChain concept poster.

## Run on Windows (easiest)
Install Python 3.11 or newer with Add Python to PATH selected.
Extract the ZIP fully. Open Saudi_HeritageChain and double-click run_windows.bat.
The first run downloads free dependencies; no paid API/key is needed.
Your browser should open http://localhost:8501. Stop with Ctrl+C.

## PowerShell (manual)
Open PowerShell inside the extracted Saudi_HeritageChain folder (where app.py is).
Run each command separately:
```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```
No virtual environment activation or execution-policy change is needed.
If python is unavailable use `py -3 -m venv .venv` for the first command.
If your prompt shows C:\Users\unita, first change to the extracted project folder.
If the .venv python is missing, check the venv creation error before proceeding.

## Linux / macOS
```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m streamlit run app.py
```

## Demo walkthrough
1. Dashboard shows two clearly fictional sample artifacts.
2. Register artifact: enter name, museum, location and unique simulated tag; optionally hash a photo.
3. Cultural passport: view the record/history; download JSON and QR.
4. Movement & custody: record destination, custody, conservation, exhibition or insurance notes.
5. Verification & alerts: use DEMO-NFC-001 for the sample pottery. Try a wrong tag, missing permit, humidity 80 or unexpected route to trigger findings.
6. Ledger audit: validate hash links and compare registry state with the ledger; export all events.

## Architecture
app.py: Streamlit user interface.
core.py: SQLite persistence, registration, event logging, hash-chain auditing and risk rules.
data/heritage.db: created automatically on first launch. Back up this file with the app stopped.
requirements.txt: dependencies. run_windows.bat: setup/launcher.

All SQL parameters use placeholders. Registry updates and ledger additions use a single transaction.
Reference photos are not stored: only a SHA-256 file hash is retained. Photo-byte equality is not visual similarity or authenticity verification.

## Boundaries and future integrations
Local demo only; do not expose publicly or store sensitive records. No authentication, encryption, official signing or distributed consensus is implemented.
The local SHA-256 chain detects inconsistent event edits and record changes, but cannot stop an administrator rewriting all hashes or deleting the end of the chain.
Nano DNA, quantum dots, spectroscopy, microengraving, RFID/NFC hardware, UNESCO/INTERPOL/customs links and accreditation are simulated identifiers/future integrations, not functioning integrations.
Risk evaluation is rule-based, not trained AI or a probability of forgery. Production ML requires labeled images, validated models, calibration and human review.
Digital museum/3D twins, international artifact loans and live border alerts require additional systems. No alert is sent externally.
QR is a demo JSON payload rather than an encrypted sovereign passport.
No official Saudi government affiliation is claimed.

## Tests
Run `python -m unittest discover -s tests -v` after setup.


## New: local blockchain protection
Each new registry or history event automatically creates a block with event hash, previous block hash, timestamp, nonce and SHA-256 proof of work (difficulty 2).
The Blockchain protection page validates block links, mining proofs and event payload commitments. Invalid chains block new writes.
Download an external checkpoint and keep it separately. Re-upload it later to detect changes or truncation at/before the checkpoint. It is not a signature, and changes after that checkpoint are not externally anchored.
A copied old data/heritage.db can be explicitly migrated from the Blockchain protection page after the legacy ledger audit passes. Migration is not retroactive proof of authenticity.
No tokens, wallets, paid services or public-chain transaction fees are needed. This is a local blockchain simulation with proof of work, not a distributed or sovereign blockchain. It does not encrypt records, physically secure artifacts, validate authenticity, or prevent a local administrator rewriting the entire chain.


## Interface refresh
The interface follows the supplied dashboard design with green/gold branding, cream background, summary cards and a styled passport. Read-only charts display counts from the existing records. All registration, history, risk, download and blockchain functions remain the same.

### Upgrade an existing installation without losing your records
Stop Streamlit with Ctrl+C. Extract this ZIP to a separate folder. Copy only its Saudi_HeritageChain/app.py into your existing project, replacing the old app.py. Keep your existing data folder, core.py and virtual environment. Restart the app as before. No new dependencies are required.
