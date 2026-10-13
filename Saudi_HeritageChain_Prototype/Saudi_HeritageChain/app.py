import hashlib
import io
import json
from html import escape
import qrcode
import streamlit as st
from core import blocks, checkpoint, check_checkpoint, migrate_legacy, verify_blocks, artifacts, assess, events, record, register, seed, verify

st.set_page_config(page_title='Saudi HeritageChain', page_icon='🏛️', layout='wide')
st.markdown("""
<style>
:root {--hc-green:#073e31;--hc-gold:#b99451;--hc-ink:#19342c;--hc-muted:#728078;}
.stApp {background:#f5f2e9;color:var(--hc-ink);font-family:Arial,Tahoma,sans-serif;}
[data-testid="stMainBlockContainer"] {max-width:1500px;padding:2rem 2.5rem 3rem;}
h1,h2,h3 {color:var(--hc-green);letter-spacing:-.02em;}
[data-testid="stSidebar"] {background:#fffdf8;border-right:1px solid #e4decc;}
[data-testid="stSidebar"] [data-testid="stSidebarContent"] {padding-top:1rem;}
.hc-brand {padding:22px 8px 24px;border-bottom:1px solid #e4decc;margin-bottom:20px;}
.hc-brand small {display:block;color:#97702a;font-weight:700;letter-spacing:.15em;font-size:10px;margin-bottom:12px;}
.hc-brand strong {display:block;color:#073e31;font-size:23px;line-height:1.2;}
.hc-brand p {color:#728078;font-size:12px;line-height:1.6;margin:12px 0 0;}
[data-testid="stSidebar"] [role="radiogroup"] {gap:8px;}
[data-testid="stSidebar"] [role="radiogroup"] label {padding:11px 12px;border-radius:10px;transition:background .15s;}
[data-testid="stSidebar"] [role="radiogroup"] label:hover {background:#edf2ec;}
[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) {background:#073e31;color:#fff;}
[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) p {color:#fff;}
.hc-header {display:flex;justify-content:space-between;align-items:center;gap:22px;padding:28px 32px;background:linear-gradient(115deg,#052b23,#0c5a45);border-bottom:4px solid #b99451;border-radius:16px;margin-bottom:22px;color:white;}
.hc-header h1 {color:white;font-size:30px;line-height:1.25;letter-spacing:-.025em;margin:0;padding:0;}
.hc-header p {color:#e6d9ba;font-size:14px;line-height:1.7;margin:10px 0 0;}
.hc-label {font-size:11px;letter-spacing:.12em;color:#e2c78e;margin-bottom:8px;text-transform:uppercase;}
.hc-demo {border:1px solid #bd9c60;color:#f4e4bb;padding:10px 16px;border-radius:24px;white-space:nowrap;font-size:12px;}
.hc-hero {background:linear-gradient(110deg,#073e31,#175f49);padding:26px 30px;border-radius:16px;color:white;margin:4px 0 24px;position:relative;overflow:hidden;}
.hc-hero h2 {color:#fff;font-size:25px;margin:0;padding:0;line-height:1.35;}
.hc-hero p {color:#deeadf;max-width:780px;font-size:14px;line-height:1.8;margin:10px 0 0;}
.hc-hero .hc-arabic {font-size:15px;color:#e3c991;margin:0 0 8px;}
[data-testid="stMetric"] {background:#fff;border:1px solid #e4decc;border-top:3px solid #b99451;padding:20px 24px;border-radius:14px;box-shadow:0 4px 18px #102e2008;}
[data-testid="stMetricLabel"] {color:#728078;font-size:13px;}
[data-testid="stMetricValue"] {color:#073e31;font-weight:700;}
[data-testid="stVerticalBlockBorderWrapper"] > div {border-color:#e4decc!important;border-radius:16px!important;background:#fff;}
[data-testid="stForm"] {background:#fff;border:1px solid #e4decc;border-radius:16px;padding:24px;}
[data-testid="stTextInput"] input,[data-testid="stTextArea"] textarea {background:#fff;border:1px solid #d6d9d0;border-radius:9px;color:#19342c;}
[data-baseweb="select"] > div {background:#fff;border-radius:9px;border-color:#d6d9d0;}
[data-testid="stButton"] button,[data-testid="stFormSubmitButton"] button,[data-testid="stDownloadButton"] button {background:#073e31;color:#fff;border:1px solid #073e31;border-radius:9px;padding:.55rem 1rem;font-weight:600;}
[data-testid="stButton"] button:hover,[data-testid="stFormSubmitButton"] button:hover,[data-testid="stDownloadButton"] button:hover {background:#0c5a45;color:#fff;border-color:#0c5a45;}
[data-testid="stButton"] button:focus-visible,[data-testid="stDownloadButton"] button:focus-visible {outline:3px solid #b99451;outline-offset:3px;}
[data-testid="stAlert"] {border-radius:12px;font-size:13px;}
[data-testid="stDataFrame"] {border:1px solid #e4decc;border-radius:12px;overflow:hidden;}
.hc-heading {color:#073e31;font-size:20px;font-weight:700;margin:4px 0 8px;}
.hc-subtitle {color:#728078;font-size:13px;margin:0 0 18px;line-height:1.7;}
.hc-process {display:grid;grid-template-columns:repeat(5,1fr);gap:12px;}
.hc-process div {background:#f2f5ef;border-left:3px solid #b99451;border-radius:9px;padding:16px;color:#19342c;font-size:13px;}
.hc-process b {display:block;color:#97702a;margin-bottom:8px;font-size:18px;}
.hc-passport {background:linear-gradient(140deg,#06382c,#0d5c46);border:3px double #b99451;border-radius:16px;padding:26px;margin:0 0 20px;color:#ead8ae;}
.hc-passport h3 {color:#f1dba3;font-size:20px;padding:0;margin:8px 0 18px;}
.hc-passport .hc-passport-name {font-size:24px;color:white;line-height:1.4;margin:10px 0;}
.hc-passport code {background:transparent;color:#f3e4c2;font-size:14px;padding:0;}
.hc-passport p {font-size:13px;line-height:1.8;margin:6px 0;color:#dfebdf;}
.hc-footer {padding-top:24px;margin-top:32px;border-top:1px solid #e4decc;color:#728078;font-size:12px;}
@media(max-width:900px){[data-testid="stMainBlockContainer"]{padding:1rem;}.hc-header{padding:22px;flex-wrap:wrap;}.hc-header h1{font-size:25px;}.hc-process{grid-template-columns:repeat(2,1fr);}.hc-demo{white-space:normal;}}
@media(max-width:520px){.hc-process{grid-template-columns:1fr;}.hc-hero{padding:22px;}}
</style>
<div class="hc-header">
 <div><div class="hc-label">Heritage documentation workspace</div><h1>Saudi HeritageChain</h1><p lang="ar" dir="rtl">سلسلة التراث السعودي · حماية الآثار وتوثيقها وتتبعها</p></div>
 <div class="hc-demo">LOCAL PROTOTYPE / DEMO DATA</div>
</div>
""", unsafe_allow_html=True)
with st.expander('About this demonstration', expanded=False):
    st.info('Local demonstration using synthetic records. Fingerprints and sensor readings are simulated. The blockchain uses local SHA-256 blocks with demonstration proof of work; it has no independent nodes and is not an official certificate. Checks are explainable rules, not trained AI.')
st.sidebar.markdown('<div class="hc-brand"><small>SAUDI HERITAGECHAIN</small><strong>Heritage<br>protection workspace</strong><p lang="ar" dir="rtl">تراثنا هويتنا، وإرثنا للأجيال</p></div>', unsafe_allow_html=True)
seed()
items = artifacts()
page = st.sidebar.radio('Workspace', ['Dashboard','Register artifact','Cultural passport','Movement & custody','Verification & alerts','Ledger audit','Blockchain protection'])
st.sidebar.caption('التراث السعودي • Saudi heritage')
if page == 'Dashboard':
    st.markdown('<div class="hc-hero"><p class="hc-arabic" lang="ar" dir="rtl">تراثنا هويتنا، وإرثنا محمي للأجيال</p><h2>Artifact documentation and protection</h2><p>Explore registered artifacts, review their custody history and inspect the integrity of the local records. Select a workspace from the sidebar to register, verify or audit an artifact.</p></div>', unsafe_allow_html=True)
    a,b,c = st.columns(3)
    a.metric('Registered artifacts',len(items)); b.metric('Recorded events',len(events())); c.metric('Locations',len({x['location'] for x in items}))
    st.write('')
    category_panel, activity_panel = st.columns(2)
    with category_panel, st.container(border=True):
        st.markdown('<div class="hc-heading">Artifacts by category</div><p class="hc-subtitle">Distribution of the current registry</p>', unsafe_allow_html=True)
        category_counts = {}
        for artifact in items:
            category_counts[artifact['category']] = category_counts.get(artifact['category'], 0) + 1
        st.bar_chart(category_counts, color='#0c5a45', height=230)
    with activity_panel, st.container(border=True):
        st.markdown('<div class="hc-heading">Recorded activity</div><p class="hc-subtitle">Events grouped by type across the registry</p>', unsafe_allow_html=True)
        event_counts = {}
        for event in events():
            event_counts[event['kind']] = event_counts.get(event['kind'], 0) + 1
        st.bar_chart(event_counts, color='#b99451', height=230)
    with st.container(border=True):
        st.markdown('<div class="hc-heading">Artifact registry</div><p class="hc-subtitle">Search the existing records and export the full registry</p>', unsafe_allow_html=True)
        query = st.text_input('Search by name, ID, custodian or location')
        selected = [x for x in items if query.lower() in json.dumps(x,ensure_ascii=False).lower()]
        st.dataframe([{k:v for k,v in x.items() if k != 'image_hash'} for x in selected],width='stretch')
        st.download_button('Export registry JSON',json.dumps(items,indent=2,ensure_ascii=False),'registry.json','application/json')
    with st.container(border=True):
        st.markdown('<div class="hc-heading">Documentation workflow</div><p class="hc-subtitle">The existing prototype workflow</p><div class="hc-process"><div><b>01</b>Register artifact</div><div><b>02</b>View passport</div><div><b>03</b>Log custody</div><div><b>04</b>Run checks</div><div><b>05</b>Audit records</div></div>', unsafe_allow_html=True)
elif page == 'Register artifact':
    with st.form('register'):
        name = st.text_input('Artifact name'); category = st.selectbox('Category',['Pottery','Manuscript','Coin','Sculpture','Other'])
        owner = st.text_input('Custodian / museum'); location = st.text_input('Current location')
        tag = st.text_input('Simulated nano / RFID / NFC fingerprint identifier')
        photo = st.file_uploader('Reference image (optional)',type=['png','jpg','jpeg'])
        submit = st.form_submit_button('Register and seal record')
    if submit:
        try:
            aid=register(name,category,owner,location,tag,hashlib.sha256(photo.getvalue()).hexdigest() if photo else '')
            st.success('Registered: '+aid)
        except ValueError as e: st.error(str(e))
else:
    aid=st.selectbox('Artifact',[x['id'] for x in items],format_func=lambda v: next(x['name']+' · '+v for x in items if x['id']==v))
    item=next(x for x in items if x['id']==aid)
    if page == 'Cultural passport':
        st.subheader('Smart cultural passport — DEMO')
        st.markdown('<div class="hc-passport"><div class="hc-label">SMART CULTURAL PASSPORT / DEMO</div><h3 lang="ar" dir="rtl">جواز السفر الثقافي الذكي</h3><div class="hc-passport-name">' + escape(item['name']) + '</div><code>' + escape(item['id']) + '</code><p>Custodian: ' + escape(item['owner']) + '<br>Location: ' + escape(item['location']) + '<br>Condition: ' + escape(item['condition']) + '</p></div>', unsafe_allow_html=True)
        st.json(item)
        passport=dict(type='DEMO cultural passport',official=False,artifact=item,history=events(aid))
        buf=io.BytesIO(); qrcode.make(json.dumps({'type':'demo','id':aid,'tag':item['tag']})).save(buf,format='PNG')
        st.image(buf.getvalue(),width=180)
        st.caption('QR contains a local demo ID and tag; it does not open an official registry or certify authenticity.')
        st.download_button('Download passport',json.dumps(passport,indent=2,ensure_ascii=False),aid+'_passport.json','application/json')
        st.download_button('Download QR',buf.getvalue(),aid+'_qr.png','image/png')
        st.dataframe(events(aid),width='stretch')
    elif page == 'Movement & custody':
        with st.form('event'):
            kind=st.selectbox('Event type',['Movement','Custody transfer','Conservation','Exhibition','Insurance'])
            destination=st.text_input('Destination (required for movement)')
            custodian=st.text_input('New custodian (required for transfer)')
            condition=st.selectbox('Condition',['Good','Needs inspection','Under restoration'])
            permit=st.text_input('Permit / reference number')
            notes=st.text_area('Notes (required)')
            submitted=st.form_submit_button('Save event')
        if submitted:
            if not notes.strip() or (kind=='Movement' and not destination.strip()) or (kind=='Custody transfer' and not custodian.strip()):
                st.error('Enter notes and the destination or new custodian where required.')
            else:
                record(aid,kind,dict(destination=destination.strip(),custodian=custodian.strip(),condition=condition,permit=permit,notes=notes.strip()))
                st.success('Event saved. Select Cultural passport to view the updated record.')
    elif page == 'Verification & alerts':
        st.caption('Decision-support rules only. Thresholds are illustrative and must be calibrated for each material. No customs or police notification is sent.')
        with st.form('check'):
            tag=st.text_input('Observed fingerprint / tag')
            temperature=st.number_input('Temperature °C',value=22.0)
            humidity=st.number_input('Relative humidity %',min_value=0.0,max_value=100.0,value=45.0)
            permit=st.checkbox('Valid movement permit confirmed',value=True)
            route=st.checkbox('Unexpected route / location detected')
            photo=st.file_uploader('Comparison photo (optional)',type=['png','jpg','jpeg'])
            run=st.form_submit_button('Run demo verification')
        if run:
            result=assess(item,tag,temperature,humidity,permit,route,hashlib.sha256(photo.getvalue()).hexdigest() if photo else '')
            st.metric('Rule-based risk score',str(result['score'])+'/100',delta=result['level'],delta_color='off')
            for text in result['findings']: st.write('• '+text)
            record(aid,'Verification',result)
            st.download_button('Download assessment',json.dumps(result,indent=2),aid+'_assessment.json','application/json')
    elif page == 'Ledger audit':
        ok,message=verify()
        (st.success if ok else st.error)(message)
        st.caption('Audit covers the entire database. A local administrator can rewrite the full chain or delete its tail. Production needs external checkpoints, signatures, access control and independent nodes.')
        st.dataframe(events(aid),width='stretch')
        st.download_button('Export complete ledger',json.dumps(events(),indent=2,ensure_ascii=False),'ledger.json','application/json')

    elif page == 'Blockchain protection':
        st.subheader('Blockchain protection — local demo')
        valid, message = verify_blocks()
        (st.success if valid else st.error)(message)
        st.caption('Each event is committed in a linked block with a nonce and two-zero SHA-256 proof of work. This low difficulty demonstrates mining; it is not production consensus.')
        chain = blocks()
        st.metric('Sealed blocks', len(chain))
        st.dataframe(chain, width='stretch')
        st.download_button('Export blockchain', json.dumps(chain,indent=2), 'blockchain.json','application/json')
        if valid:
            st.download_button('Save external checkpoint',json.dumps(checkpoint(),indent=2),'heritage_checkpoint.json','application/json')
        st.write('Keep checkpoints separately from the database. Upload an older trusted checkpoint to detect rewriting or deletion before that checkpoint.')
        uploaded = st.file_uploader('Previously saved checkpoint',type=['json'])
        if uploaded:
            try:
                ok, result = check_checkpoint(json.loads(uploaded.getvalue()))
                (st.success if ok else st.error)(result)
            except (ValueError,UnicodeError): st.error('Invalid JSON checkpoint.')
        if not chain and events():
            st.warning('Existing events predate blockchain protection. Migration seals their current state; it cannot prove earlier authenticity.')
            if st.button('Seal legacy events into blocks'):
                try:
                    migrate_legacy(); st.rerun()
                except ValueError as error: st.error(str(error))
        st.info('No distributed network, signatures or encryption is provided. A database administrator can still rewrite the entire chain. Checkpoints detect changes only when a trusted earlier copy is retained elsewhere; records after that checkpoint remain unanchored.')

st.markdown('<div class="hc-footer">SAUDI HERITAGECHAIN · Local software prototype · Demonstration records · No official accreditation</div>', unsafe_allow_html=True)
