import streamlit as st
import pandas as pd
from utils_frontend import login, register, current_user, search, sync_redcap

st.set_page_config(page_title="Linkage UI")


def render_login():
    st.title("Login")
    with st.form("login"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")
        if submitted:
            resp = login(email, password)
            if resp.status_code == 200:
                st.session_state["token"] = resp.json()["access_token"]
                st.experimental_rerun()
            else:
                st.error("Login failed")
    st.write("---")
    st.subheader("Register")
    with st.form("register"):
        name = st.text_input("Name")
        remail = st.text_input("Email", key="reg_email")
        rpassword = st.text_input("Password", type="password", key="reg_password")
        if st.form_submit_button("Register"):
            resp = register(remail, rpassword, name)
            if resp.status_code == 200:
                st.success("Registered. Please log in.")
            else:
                st.error("Registration failed")


def render_match(token: str):
    st.title("Record Match")
    with st.form("match"):
        first = st.text_input("Mother first name")
        last = st.text_input("Mother last name")
        sex = st.selectbox("Sex", ["", "F", "M", "U", "I"], index=0)
        dob = st.date_input("DOB", value=None)
        address = st.text_input("Address")
        phone1 = st.text_input("Phone 1")
        phone2 = st.text_input("Phone 2")
        cluster = st.text_input("Cluster")
        submitted = st.form_submit_button("Search")
        if submitted:
            payload = {
                "record": {
                    "first_name": first,
                    "last_name": last,
                    "sex": sex,
                    "dob": dob.isoformat() if dob else None,
                    "address": address,
                    "phone1": phone1,
                    "phone2": phone2,
                    "cluster": cluster,
                }
            }
            resp = search(token, payload)
            if resp.status_code == 200:
                data = resp.json()
                if data:
                    st.dataframe(pd.DataFrame(data))
                else:
                    st.info("No matches")
            else:
                st.error("Search failed")


def render_data_admin(token: str):
    st.title("Admin Data")
    if st.button("Sync from REDCap"):
        resp = sync_redcap(token)
        if resp.status_code == 200:
            st.success("Sync completed")
        else:
            st.error("Sync failed")


def render_profile(token: str):
    resp = current_user(token)
    if resp.status_code != 200:
        st.error("Auth error")
        return
    user = resp.json()
    st.title("Profile")
    st.json(user)
    if st.button("Logout"):
        st.session_state.pop("token", None)
        st.experimental_rerun()


def main():
    token = st.session_state.get("token")
    if not token:
        render_login()
        return
    resp = current_user(token)
    if resp.status_code != 200:
        render_login()
        return
    user = resp.json()
    pages = {"Match": render_match, "Profile": render_profile}
    if user.get("role") == "admin":
        pages["Data"] = render_data_admin
    choice = st.sidebar.selectbox("Page", list(pages.keys()))
    pages[choice](token)


if __name__ == "__main__":
    main()
