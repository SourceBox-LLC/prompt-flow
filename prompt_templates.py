import streamlit as st
import json
from llm import call_llm
from auth import login_page, logout  # Import auth functions


def prompt_templates_app():
    """
    Renders the Prompt Templates UI.
    """
    # 1. Back button to go to main page
    if st.sidebar.button("Back to Main App"):
        st.session_state["page"] = "home"
        st.rerun()
    
    # Display login status and controls in the sidebar
    with st.sidebar:
        st.write("---")
        st.write("### Authentication")
        
        # Show login status
        is_logged_in = st.session_state.get("logged_in", False)
        st.write(f"**Status:** {'👤 Logged In' if is_logged_in else '🔒 Not Logged In'}")
        
        # Login/Logout controls
        if not is_logged_in:
            # Always show the login form when not logged in
            st.write("### Login")
            with st.form(key="templates_login_form"):
                username = st.text_input("Username", key="templates_username")
                password = st.text_input("Password", type="password", key="templates_password")
                login_submit = st.form_submit_button("Log In")
                
                if login_submit:
                    if username and password:  # Any non-empty username/password will work
                        # Update session state directly
                        st.session_state.logged_in = True
                        st.session_state.username = username
                        st.success(f"Welcome, {username}!")
                        st.rerun()
                    else:
                        st.error("Please enter both username and password")
        else:
            # Show username and logout button
            st.write(f"**User:** {st.session_state.get('username', 'User')}")
            if st.button("🚪 Logout", use_container_width=True):
                # Clear session state on logout
                st.session_state.logged_in = False
                st.session_state.username = None
                st.session_state.access_token = None
                st.success("Logged out successfully")
                st.rerun()
        
        st.write("---")

    st.title("Prompt Tester with AWS Bedrock")

    st.subheader("Template Name")
    template_name = st.text_input("Enter a name for your template", "Template 1")

    st.subheader("Prompt Template")
    prompt_template = st.text_area(
        "Enter your prompt with placeholders. (e.g. 'Hello, my name is {name}.')",
        value="Hello, my name is {name}. I love {hobby}."
    )

    st.subheader("Placeholder Values")
    placeholder_json = st.text_area(
        "Enter your placeholder values in JSON format. "
        "(e.g. {\"name\": \"Alice\", \"hobby\": \"coding\"})",
        value='{"name": "Alice", "hobby": "coding"}'
    )

    # Replace text input with a select box that only has one option
    model_name = st.selectbox(
        "Model Name",
        ["anthropic.claude-3-sonnet-20240229-v1:0"]
    )

    temperature = st.slider(
        "Temperature", 
        min_value=0.0, max_value=1.0, value=0.7, step=0.1
    )

    if st.button("Save Template"):
        if "templates" not in st.session_state:
            st.session_state["templates"] = {}

        st.session_state["templates"][template_name] = {
            "prompt_template": prompt_template,
            "placeholder_json": placeholder_json,
            "model_name": model_name,
            "temperature": temperature,
        }

        st.success(f"Template '{template_name}' has been saved!")

    if "templates" in st.session_state and st.session_state["templates"]:
        st.subheader("Saved Templates")
        for temp_name in list(st.session_state["templates"].keys()):
            col1, col2 = st.columns([4, 1])
            with col1:
                st.write(f"**{temp_name}**")
            with col2:
                if st.button("Delete", key=f"delete_{temp_name}"):
                    del st.session_state["templates"][temp_name]
                    st.success(f"Template '{temp_name}' has been deleted!")
                    st.rerun()

    with st.sidebar:
        st.title("Prompt Tester with AWS Bedrock")
        st.subheader("Prompt Template")

    if st.sidebar.button("Generate"):
        try:
            placeholders = json.loads(placeholder_json)
            final_prompt = prompt_template.format(**placeholders)
        except Exception as e:
            st.error(f"Error parsing JSON or injecting variables: {e}")
            final_prompt = None

        if final_prompt:
            st.sidebar.write("### Final Prompt:")
            st.sidebar.code(final_prompt, language="markdown")

            output = call_llm(
                prompt=final_prompt,
                model=model_name,
                temperature=temperature
            )

            st.sidebar.write("### Model Output:")
            st.sidebar.write(output)
