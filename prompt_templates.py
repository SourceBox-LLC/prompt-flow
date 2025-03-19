import streamlit as st
import json
from llm import call_llm
from auth import login_page, logout, login_user  # Import auth functions
import time

def prompt_templates_app():
    """
    Renders the Prompt Templates UI with an enhanced professional design.
    """
    # Custom CSS for styling
    st.markdown("""
    <style>
    .main .block-container {padding-top: 2rem;}
    .stTabs [data-baseweb="tab-list"] {gap: 2rem;}
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        border-radius: 4px 4px 0px 0px;
        padding: 10px 16px;
        font-weight: 500;
    }
    .stTabs [aria-selected="true"] {
        background-color: #f0f2f6;
        border-bottom: 3px solid #4e8df5;
    }
    div.stButton > button {height: 40px;}
    .css-1r6slb0 {border: 1px solid #ddd; padding: 12px; border-radius: 5px;}
    .sidebar-content {padding: 10px;}
    .template-card {
        background-color: #f9f9f9;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 15px;
        border-left: 4px solid #4e8df5;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Initialize session state variables if not present
    if "templates" not in st.session_state:
        st.session_state["templates"] = {}
    if "active_template" not in st.session_state:
        st.session_state["active_template"] = None
    if "model_output" not in st.session_state:
        st.session_state["model_output"] = ""
    if "final_prompt" not in st.session_state:
        st.session_state["final_prompt"] = ""
    
    # Handle navigation
    if st.sidebar.button("← Back to Main App", use_container_width=True):
        st.session_state["page"] = "home"  # Explicitly set to home
        st.rerun()
    
    # Authentication section in sidebar
    with st.sidebar:
        st.markdown("---")
        st.markdown("### Account")
        
        # Show login status
        is_logged_in = st.session_state.get("logged_in", False)
        status_col1, status_col2 = st.columns([1, 3])
        with status_col1:
            st.markdown("**Status:**")
        with status_col2:
            if is_logged_in:
                st.markdown("👤 Logged In")
            else:
                st.markdown("🔒 Not Logged In")
        
        # Login/Logout controls
        if not is_logged_in:
            with st.expander("Log In", expanded=True):
                with st.form(key="templates_login_form", border=False):
                    username = st.text_input("Username or Email", key="templates_username")
                    password = st.text_input("Password", type="password", key="templates_password")
                    login_submit = st.form_submit_button("Log In", use_container_width=True)
                    
                    if login_submit:
                        if username and password:
                            with st.spinner("Logging in..."):
                                # Use the new login_user function from auth module
                                if login_user(username, password):
                                    st.success(f"Welcome, {st.session_state.username}!")
                                    st.rerun()
                                else:
                                    st.error("Invalid username or password")
                        else:
                            st.error("Please enter both username/email and password")
        else:
            # Show username and logout button
            user_info = f"**User:** {st.session_state.username}"
            if st.session_state.get("premium_status", False):
                user_info += " ⭐ Premium"
            st.markdown(user_info)
            
            if st.button("🚪 Logout", key="templates_logout_btn", use_container_width=True):
                with st.spinner("Logging out..."):
                    time.sleep(0.3)  # Simulate logout request
                    # Clear session state on logout
                    logout()
                    st.success("Logged out successfully")
                    st.rerun()
        
        st.markdown("---")
        
        # Output section in sidebar
        st.markdown("### Model Output")
        
        if st.session_state["final_prompt"]:
            with st.expander("Final Prompt", expanded=False):
                st.code(st.session_state["final_prompt"], language="markdown")
        
        if st.session_state["model_output"]:
            st.markdown("#### Response:")
            st.markdown(st.session_state["model_output"])
        else:
            st.info("Generate a response using the controls in the main panel")
    
    # Main content area
    st.markdown("# 🤖 Prompt Engineer Workbench")
    st.markdown("Design, test, and save prompt templates with AWS Bedrock models")
    
    # Create tabs for different sections
    tab1, tab2, tab3 = st.tabs(["📝 Template Editor", "🔍 Prompt Tester", "💾 Saved Templates"])
    
    with tab1:
        st.markdown("### Template Design")
        template_col1, template_col2 = st.columns([3, 1])
        
        with template_col1:
            template_name = st.text_input("Template Name", value="Template 1", 
                                        placeholder="Enter a descriptive name")
        
        with template_col2:
            model_name = st.selectbox(
                "Model",
                ["anthropic.claude-3-sonnet-20240229-v1:0"],
                help="Select the AI model to use for this template"
            )
        
        prompt_template = st.text_area(
            "Prompt Template",
            value="Hello, my name is {name}. I love {hobby}.",
            height=200,
            placeholder="Enter your prompt with placeholders. (e.g. 'Hello, my name is {name}.')",
            help="Use {placeholder} syntax for variables that will be filled during execution"
        )
        
        param_col1, param_col2 = st.columns([3, 1])
        
        with param_col1:
            placeholder_json = st.text_area(
                "Parameter Values (JSON)",
                value='{"name": "Alice", "hobby": "coding"}',
                height=150,
                placeholder='{"name": "Alice", "hobby": "coding"}'
            )
        
        with param_col2:
            st.markdown("#### Generation Settings")
            temperature = st.slider(
                "Temperature", 
                min_value=0.0, max_value=1.0, value=0.7, step=0.1,
                help="Higher values produce more creative but less predictable results"
            )
            
            st.markdown("#### Template Actions")
            save_col1, save_col2 = st.columns(2)
            
            with save_col1:
                if st.button("💾 Save Template", use_container_width=True):
                    if template_name.strip():
                        st.session_state["templates"][template_name] = {
                            "prompt_template": prompt_template,
                            "placeholder_json": placeholder_json,
                            "model_name": model_name,
                            "temperature": temperature,
                        }
                        st.success(f"Template '{template_name}' saved!")
                    else:
                        st.error("Please provide a template name")
            
            with save_col2:
                if st.button("🧪 Test Template", use_container_width=True):
                    try:
                        placeholders = json.loads(placeholder_json)
                        final_prompt = prompt_template.format(**placeholders)
                        st.session_state["final_prompt"] = final_prompt
                        
                        with st.spinner("Generating response..."):
                            output = call_llm(
                                prompt=final_prompt,
                                model=model_name,
                                temperature=temperature
                            )
                            st.session_state["model_output"] = output
                        
                        st.success("Response generated!")
                    except json.JSONDecodeError:
                        st.error("Invalid JSON format for parameters")
                    except KeyError as e:
                        st.error(f"Missing placeholder in parameters: {e}")
                    except Exception as e:
                        st.error(f"Error: {e}")

    with tab2:
        st.markdown("### Prompt Testing Lab")
        
        test_col1, test_col2 = st.columns([2, 1])
        
        with test_col1:
            st.markdown("#### Prompt Input")
            test_prompt = st.text_area(
                "Enter your prompt",
                value=st.session_state.get("final_prompt", "Write a short story about a robot."),
                height=250
            )
        
        with test_col2:
            st.markdown("#### Test Settings")
            test_model = st.selectbox(
                "Model",
                ["anthropic.claude-3-sonnet-20240229-v1:0"],
                key="test_model"
            )
            
            test_temp = st.slider(
                "Temperature", 
                min_value=0.0, max_value=1.0, value=0.7, step=0.1,
                key="test_temp"
            )
            
            st.markdown("#### Actions")
            if st.button("🚀 Generate Response", use_container_width=True):
                with st.spinner("Generating response..."):
                    st.session_state["final_prompt"] = test_prompt
                    output = call_llm(
                        prompt=test_prompt,
                        model=test_model,
                        temperature=test_temp
                    )
                    st.session_state["model_output"] = output
                st.success("Response generated!")
        
        if st.session_state.get("model_output"):
            st.markdown("#### Preview:")
            with st.expander("View Response", expanded=True):
                st.markdown(st.session_state["model_output"])

    with tab3:
        st.markdown("### Template Library")
        
        if not st.session_state["templates"]:
            st.info("No templates saved yet. Create a new template in the Template Editor tab.")
        else:
            # Search box for templates
            st.text_input("🔍 Search templates", key="template_search", 
                        placeholder="Type to filter templates...")
            
            search_term = st.session_state.get("template_search", "").lower()
            filtered_templates = {
                name: template for name, template in st.session_state["templates"].items()
                if search_term in name.lower()
            }
            
            # Display templates in a grid
            cols = st.columns(2)
            for idx, (temp_name, temp_data) in enumerate(filtered_templates.items()):
                col = cols[idx % 2]
                with col:
                    with st.container(border=True):
                        st.markdown(f"**{temp_name}**")
                        st.text_area(
                            "Prompt",
                            value=temp_data["prompt_template"],
                            height=100,
                            disabled=True,
                            key=f"view_{temp_name}"
                        )
                        
                        action_col1, action_col2, action_col3 = st.columns(3)
                        with action_col1:
                            if st.button("Load", key=f"load_{temp_name}", use_container_width=True):
                                # Set active template
                                st.session_state["active_template"] = temp_name
                                st.rerun()
                        
                        with action_col2:
                            if st.button("Run", key=f"run_{temp_name}", use_container_width=True):
                                try:
                                    placeholders = json.loads(temp_data["placeholder_json"])
                                    final_prompt = temp_data["prompt_template"].format(**placeholders)
                                    st.session_state["final_prompt"] = final_prompt
                                    
                                    with st.spinner("Generating response..."):
                                        output = call_llm(
                                            prompt=final_prompt,
                                            model=temp_data["model_name"],
                                            temperature=temp_data["temperature"]
                                        )
                                        st.session_state["model_output"] = output
                                    
                                    st.success("Response generated!")
                                except Exception as e:
                                    st.error(f"Error: {e}")
                        
                        with action_col3:
                            if st.button("Delete", key=f"delete_{temp_name}", use_container_width=True):
                                del st.session_state["templates"][temp_name]
                                st.success(f"Template '{temp_name}' deleted!")
                                st.rerun()
    
    # Handle loading a template if selected
    if st.session_state["active_template"]:
        temp_name = st.session_state["active_template"]
        temp_data = st.session_state["templates"].get(temp_name)
        
        if temp_data:
            # Switch to the first tab
            st.session_state["active_template"] = None
            
            # Need to use query params or another approach to activate the tab
            # For now, we'll show a notification
            st.info(f"Template '{temp_name}' loaded in the Template Editor tab")
            
            # Update the values
            template_name = temp_name
            prompt_template = temp_data["prompt_template"]
            placeholder_json = temp_data["placeholder_json"]
            model_name = temp_data["model_name"]
            temperature = temp_data["temperature"]
            
            # Trigger a rerun to update the UI
            st.rerun()
