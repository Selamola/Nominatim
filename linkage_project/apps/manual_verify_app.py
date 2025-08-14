import streamlit as st
import pandas as pd
from pathlib import Path
import datetime

DATA_DIR = Path(__file__).resolve().parents[1] / 'data'
OUTPUTS = DATA_DIR / 'outputs'
TEMP = DATA_DIR / 'temp'
PARTIAL_FILE = DATA_DIR / 'temp' / 'partial_verified_matches.csv'

st.set_page_config(page_title="Manual Verification")

st.title("Manual Verification")

uploaded = st.file_uploader("Upload CSV", type='csv')
if uploaded is not None:
    data = pd.read_csv(uploaded)
else:
    sample_path = OUTPUTS / 'sample_for_verification.csv'
    if sample_path.exists():
        data = pd.read_csv(sample_path)
    else:
        st.stop()

min_score, max_score = st.slider('Score range', 0.0, 1.0, (0.0, 1.0), 0.01)
search = st.text_input('Search REC_CODE or report_id')
mask = (data['final_score'].between(min_score, max_score))
if search:
    mask &= data['REC_CODE'].astype(str).str.contains(search) | data['report_id'].astype(str).str.contains(search)
records = data[mask].reset_index(drop=True)

if PARTIAL_FILE.exists():
    partial = pd.read_csv(PARTIAL_FILE)
else:
    partial = pd.DataFrame(columns=['df1_index', 'df2_index', 'label'])

idx = st.number_input('Record index', 0, len(records)-1, 0)
row = records.loc[int(idx)]
col1, col2 = st.columns(2)
with col1:
    st.write('**Left**')
    st.write(row.filter(like='_left'))
with col2:
    st.write('**Right**')
    st.write(row.filter(like='_right'))

label = st.radio('Label', options={'Match':1, 'Non-match':0, 'Uncertain':-1}, index=1)

if st.button('Save'):
    new_row = {'df1_index': row['df1_index'], 'df2_index': row['df2_index'], 'label': label}
    partial = partial[~((partial.df1_index==row['df1_index']) & (partial.df2_index==row['df2_index']))]
    partial = pd.concat([partial, pd.DataFrame([new_row])])
    PARTIAL_FILE.parent.mkdir(parents=True, exist_ok=True)
    partial.to_csv(PARTIAL_FILE, index=False)
    st.success('Saved')

if len(partial) >= 10:
    partial.to_csv(PARTIAL_FILE, index=False)

if st.button('Finish'):
    partial.to_csv(OUTPUTS / 'verified_matches.csv', index=False)
    st.success('Final labels saved.')

st.download_button('Download partial', data=partial.to_csv(index=False), file_name='partial_verified_matches.csv')

progress = len(partial)/len(records) if len(records) else 0
st.progress(progress)
st.write(f"{len(partial)} of {len(records)} labeled")

