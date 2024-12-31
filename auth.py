import streamlit as st
from config import load_config, verify_password, hash_password, save_config

def init_auth():
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'username' not in st.session_state:
        st.session_state.username = None
    if 'client' not in st.session_state:
        st.session_state.client = None

def login_user(username, password):
    config = load_config()
    if username in config['users']:
        if verify_password(password, config['users'][username]['password']):
            st.session_state.authenticated = True
            st.session_state.username = username
            return True
    return False

def register_user(username, password, api_key):
    config = load_config()
    if username in config['users']:
        return False, "Username already exists"
    
    config['users'][username] = {
        'password': hash_password(password),
        'api_key': api_key
    }
    save_config(config)
    return True, "Registration successful"

def logout_user():
    st.session_state.authenticated = False
    st.session_state.username = None
    st.session_state.client = None