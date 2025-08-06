import streamlit as st
import pandas as pd
from io import BytesIO
from matching import MatchConfig, prepare_database, match_records

st.set_page_config(page_title="MITS Matcher")

@st.cache_data
def load_db():
    return prepare_database('df1_saved.csv')

def main():
    st.title("MITS Record Matcher")
    db = load_db()

    with st.sidebar:
        st.header("Thresholds")
        thresholds = {
            'mom_first_name': st.slider('First Name Threshold', 0.0, 1.0, 0.85),
            'mom_last_name': st.slider('Last Name Threshold', 0.0, 1.0, 0.85),
            'address': st.slider('Address Threshold', 0.0, 1.0, 0.8),
            'sex': st.slider('Sex Threshold', 0.0, 1.0, 1.0),
            'dob': st.slider('DOB Threshold', 0.0, 1.0, 1.0),
            'phone': st.slider('Phone Threshold', 0.0, 1.0, 0.8),
            'cluster': st.slider('Cluster Threshold', 0.0, 1.0, 1.0),
        }
        st.header("Weights")
        weights = {
            'mom_first_name': st.number_input('First Name Weight', 0.0, 10.0, 1.0),
            'mom_last_name': st.number_input('Last Name Weight', 0.0, 10.0, 1.0),
            'address': st.number_input('Address Weight', 0.0, 10.0, 1.0),
            'sex': st.number_input('Sex Weight', 0.0, 10.0, 1.0),
            'dob': st.number_input('DOB Weight', 0.0, 10.0, 1.0),
            'phone': st.number_input('Phone Weight', 0.0, 10.0, 1.0),
            'cluster': st.number_input('Cluster Weight', 0.0, 10.0, 1.0),
        }
        top_n = st.number_input('Top N Results', 1, 50, 5)

    st.subheader("MITS Notification")
    with st.form("mits_input"):
        mom_first_name = st.text_input("Mother First Name")
        mom_last_name = st.text_input("Mother Last Name")
        sex = st.selectbox("Sex", ['', 'M', 'F'])
        dob = st.date_input("Date of Birth")
        address = st.text_input("Address")
        phonenumber = st.text_input("Phone Number")
        phonenumber2 = st.text_input("Phone Number 2")
        cluster = st.text_input("Cluster")
        submitted = st.form_submit_button("Search")

    results = pd.DataFrame()
    if submitted:
        mits_record = {
            'mom_first_name': mom_first_name,
            'mom_last_name': mom_last_name,
            'sex': sex,
            'dob': dob,
            'address': address,
            'phonenumber': phonenumber,
            'phonenumber2': phonenumber2,
            'cluster': cluster,
        }
        config = MatchConfig(thresholds=thresholds, weights=weights, top_n=top_n)
        results = match_records(mits_record, db, config)
        st.success(f"Found {len(results)} candidate matches")
        st.dataframe(results)

    if not results.empty:
        csv = results.to_csv(index=False).encode('utf-8')
        st.download_button("Export CSV", csv, "matches.csv", "text/csv")

        buf = BytesIO()
        results.to_excel(buf, index=False)
        st.download_button("Export Excel", buf.getvalue(), "matches.xlsx")

if __name__ == '__main__':
    main()
