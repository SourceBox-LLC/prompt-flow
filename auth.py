import streamlit as st
import boto3
import json
import logging

# --- 1) Initialize Session States ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'access_token' not in st.session_state:
    st.session_state.access_token = None
if 'username' not in st.session_state:
    st.session_state.username = None
if 'logout_trigger' not in st.session_state:
    st.session_state.logout_trigger = False

# --- 2) Initialize Boto3 Client (assuming st.secrets usage) ---
ACCESS_KEY = st.secrets["ACCESS_KEY"]
SECRET_KEY = st.secrets["SECRET_KEY"]
REGION = st.secrets["REGION"]

session = boto3.Session(
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY,
    region_name=REGION
)
lambda_client = session.client('lambda')

# --- 3) Login Page ---
def login_page():
    """Display a login form and handle user authentication."""
    st.title("Login Page")

    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit_button = st.form_submit_button("Login")

    if submit_button:
        logging.info("Login attempt for user: %s", username)
        
        # Define the payload for the Lambda function
        payload = {
            "action": "LOGIN_USER",
            "data": {
                "username": username,
                "password": password
            }
        }

        # Invoke the Lambda function
        try:
            response = lambda_client.invoke(
                FunctionName='sb-user-auth-sbUserAuthFunction-zjl3761VSGKj',  # Replace with your Lambda name
                InvocationType='RequestResponse',
                Payload=json.dumps(payload)
            )
            logging.info("Lambda function invoked successfully.")

        except Exception as e:
            logging.error("Error invoking Lambda function: %s", e)
            st.error("An error occurred while processing your request.")
            return

        # Parse the Lambda response
        response_payload = json.loads(response['Payload'].read())
        logging.info("Received response from Lambda: %s", response_payload)

        # If success, update session state
        if response_payload.get('statusCode') == 200:
            body = json.loads(response_payload['body'])
            st.session_state.logged_in = True
            st.session_state.access_token = body['token']
            st.session_state.username = username
            logging.info("User %s logged in successfully.", username)

            st.success("Logged in successfully!")
            st.rerun()  # Force re-run so we go to main page

        else:
            logging.warning("Invalid login attempt for user: %s", username)
            st.error("Invalid username or password.")

# --- 4) Logout ---
def logout():
    """Logs out the user and clears session state."""
    logging.info("User logged out.")
    st.session_state.logged_in = False
    st.session_state.access_token = None
    st.session_state.username = None
    # Toggle the logout trigger (useful if you want to force a rerun on logout)
    st.session_state.logout_trigger = not st.session_state.logout_trigger
