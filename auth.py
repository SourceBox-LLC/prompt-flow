import streamlit as st
import requests
import json
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# API Base URL - replace with your actual API URL
API_BASE_URL = "http://127.0.0.1:5000"  # Update this with your actual API endpoint

# --- Initialize Session States ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'access_token' not in st.session_state:
    st.session_state.access_token = None
if 'username' not in st.session_state:
    st.session_state.username = None
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'email' not in st.session_state:
    st.session_state.email = None
if 'premium_status' not in st.session_state:
    st.session_state.premium_status = False

def login_user(username, password):
    """
    Login with the Flask API
    
    Args:
        username (str): Username or email
        password (str): User password
    
    Returns:
        bool: True if login successful, False otherwise
    """
    try:
        # Prepare login data
        login_data = {}
        if "@" in username:  # Check if username is actually an email
            login_data = {"email": username, "password": password}
        else:
            login_data = {"username": username, "password": password}
        
        # Make API request
        response = requests.post(
            f"{API_BASE_URL}/login",
            json=login_data,
            headers={"Content-Type": "application/json"}
        )
        
        # Check if login was successful
        if response.status_code == 200:
            data = response.json()
            # Save user data in session state
            st.session_state.logged_in = True
            st.session_state.access_token = data.get('access_token')
            st.session_state.username = data.get('username')
            st.session_state.user_id = data.get('user_id')
            st.session_state.email = data.get('email')
            st.session_state.premium_status = data.get('premium_status', False)
            logger.info(f"User '{username}' logged in successfully")
            return True
        else:
            error_msg = response.json().get('message', 'Login failed')
            logger.warning(f"Login failed for '{username}': {error_msg}")
            return False
    except Exception as e:
        logger.error(f"Error during login: {str(e)}")
        return False

def register_user(email, username, password):
    """
    Register a new user with the Flask API
    
    Args:
        email (str): User email
        username (str): Username
        password (str): User password
    
    Returns:
        tuple: (success (bool), message (str))
    """
    try:
        # Prepare registration data
        register_data = {
            "email": email,
            "username": username,
            "password": password
        }
        
        # Make API request
        response = requests.post(
            f"{API_BASE_URL}/register",
            json=register_data,
            headers={"Content-Type": "application/json"}
        )
        
        # Parse response
        data = response.json()
        
        if response.status_code == 201:
            logger.info(f"User '{username}' registered successfully")
            return True, "Registration successful! You can now log in."
        else:
            error_msg = data.get('message', 'Registration failed')
            logger.warning(f"Registration failed: {error_msg}")
            return False, error_msg
    except Exception as e:
        logger.error(f"Error during registration: {str(e)}")
        return False, f"An error occurred: {str(e)}"

def get_user_profile():
    """
    Get current user profile data
    
    Returns:
        dict: User profile data or None if not logged in or error
    """
    if not st.session_state.logged_in or not st.session_state.access_token:
        return None
        
    try:
        # Make API request with JWT token
        response = requests.get(
            f"{API_BASE_URL}/user",
            headers={
                "Authorization": f"Bearer {st.session_state.access_token}",
                "Content-Type": "application/json"
            }
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            logger.warning("Failed to get user profile")
            return None
    except Exception as e:
        logger.error(f"Error getting user profile: {str(e)}")
        return None

def logout():
    """Logs out the user and clears session state."""
    logger.info("User logged out")
    
    # Clear session state
    st.session_state.logged_in = False
    st.session_state.access_token = None
    st.session_state.username = None
    st.session_state.user_id = None
    st.session_state.email = None
    st.session_state.premium_status = False

def login_page():
    """Display a login form and handle user authentication."""
    st.title("Login Page")
    
    # Create tabs for login and registration
    login_tab, register_tab = st.tabs(["Login", "Register"])
    
    with login_tab:
        with st.form("login_form"):
            username = st.text_input("Username or Email")
            password = st.text_input("Password", type="password")
            submit_button = st.form_submit_button("Login")
            
            if submit_button:
                if not username or not password:
                    st.error("Please enter both username/email and password")
                else:
                    with st.spinner("Logging in..."):
                        if login_user(username, password):
                            st.success(f"Welcome, {st.session_state.username}!")
                            st.rerun()
                        else:
                            st.error("Invalid username or password")
    
    with register_tab:
        with st.form("register_form"):
            reg_email = st.text_input("Email")
            reg_username = st.text_input("Username")
            reg_password = st.text_input("Password", type="password")
            reg_confirm_password = st.text_input("Confirm Password", type="password")
            register_button = st.form_submit_button("Register")
            
            if register_button:
                if not reg_email or not reg_username or not reg_password:
                    st.error("Please fill in all fields")
                elif reg_password != reg_confirm_password:
                    st.error("Passwords do not match")
                else:
                    with st.spinner("Registering..."):
                        success, message = register_user(reg_email, reg_username, reg_password)
                        if success:
                            st.success(message)
                        else:
                            st.error(message)
