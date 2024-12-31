# config.py
import yaml
from pathlib import Path
import bcrypt
import streamlit as st
import os

def load_config():
    config_path = Path(".streamlit/config.yaml")
    if config_path.exists():
        with open(config_path) as file:
            return yaml.safe_load(file)
    return {"users": {}}

def save_config(config):
    config_path = Path(".streamlit/config.yaml")
    config_path.parent.mkdir(exist_ok=True)
    with open(config_path, "w") as file:
        yaml.dump(config, file)

def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(password, hashed):
    return bcrypt.checkpw(password.encode(), hashed.encode())

# auth.py
def init_auth():
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'username' not in st.session_state:
        st.session_state.username = None

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

# app.py
import streamlit as st
import anthropic
from PIL import Image
import io
import base64
import json
from pathlib import Path

# Import authentication functions
from auth import init_auth, login_user, register_user, logout_user

# Initialize authentication state
init_auth()

# Authentication UI
def show_auth_ui():
    st.title("PicTunes Authentication")
    
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login")
            
            if submit:
                if login_user(username, password):
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Invalid username or password")
    
    with tab2:
        with st.form("register_form"):
            new_username = st.text_input("Username")
            new_password = st.text_input("Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            api_key = st.text_input("Anthropic API Key", type="password")
            submit = st.form_submit_button("Register")
            
            if submit:
                if new_password != confirm_password:
                    st.error("Passwords do not match")
                elif not new_username or not new_password or not api_key:
                    st.error("All fields are required")
                else:
                    success, message = register_user(new_username, new_password, api_key)
                    if success:
                        st.success(message)
                    else:
                        st.error(message)

# Main application code (your existing PicTunes code)
def main_app():
    # Initialize Anthropic client with user's API key
    config = load_config()
    api_key = config['users'][st.session_state.username]['api_key']
    client = anthropic.Client(api_key=api_key)
    
    st.title('PicTunes')
    st.text('Your AI-Powered Creative Partner for Instagram Posts')
    
    # Add logout button
    if st.sidebar.button("Logout"):
        logout_user()
        st.rerun()
    
    # Show welcome message
    st.sidebar.success(f"Welcome, {st.session_state.username}!")
    
    # Rest of your existing PicTunes code here
    # (Copy all the image processing and caption generation code here)
    # ...

# Main execution
if not st.session_state.authenticated:
    show_auth_ui()
else:
    main_app()