import streamlit as st
# Set page config at the very beginning of the script
st.set_page_config(
    page_title="Prompt Engineer Workbench",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

from barfi import st_barfi, Block
from prompt_templates import prompt_templates_app
import re  # For parsing variables from the prompt template
from langchain_community.tools.pubmed.tool import PubmedQueryRun
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper
import boto3
import json
from langchain_community.tools.tavily_search import TavilySearchResults

from auth import login_user, logout, register_user  # Update import
from llm import call_llm

###############################################################################
# 1. Define Compute Functions
###############################################################################

def invoke_anthropic(self):
    """
    Compute function for the Anthropic (Model) Block.
    """
    in_val = self.get_interface(name='input_0')
    if in_val:
        st.sidebar.write("Anthropic block received input:", in_val)
        
        # Handle input that might be a dictionary or string
        prompt = in_val['output'] if isinstance(in_val, dict) and 'output' in in_val else str(in_val)
        
        # Call the LLM using the input value
        raw_output = call_llm(prompt=prompt, model="anthropic.claude-3-sonnet-20240229-v1:0")
        
        # Format the output as JSON
        out_val = {
            "input": prompt,
            "model": "anthropic.claude-3-sonnet-20240229-v1:0",
            "output": raw_output
        }
        
        self.set_interface(name='output_0', value=out_val)
        st.sidebar.write("### Anthropic Block Output:")
        st.sidebar.json(out_val)
    else:
        st.sidebar.write("Anthropic block received no input.")


def invoke_titan(self):
    """
    Compute function for the Titan (Model) Block.
    """
    in_val = self.get_interface(name='input_0')
    if in_val:
        st.sidebar.write("Titan block received input:", in_val)
        
        # Handle input that might be a dictionary or string
        prompt = in_val['output'] if isinstance(in_val, dict) and 'output' in in_val else str(in_val)
        
        # Call the LLM using the input value
        raw_output = call_llm(prompt=prompt, model="amazon.titan-text-premier-v1:0")
        
        # Format the output as JSON
        out_val = {
            "input": prompt,
            "model": "amazon.titan-text-premier-v1:0",
            "output": raw_output
        }
        
        self.set_interface(name='output_0', value=out_val)
        st.sidebar.write("### Titan Block Output:")
        st.sidebar.json(out_val)
    else:
        st.sidebar.write("Titan block received no input.")


def invoke_meta_llama(self):
    """
    Compute function for the Meta LLama (Model) Block.
    """
    in_val = self.get_interface(name='input_0')
    if in_val:
        st.sidebar.write("Meta LLama block received input:", in_val)
        
        # Handle input that might be a dictionary or string
        prompt = in_val['output'] if isinstance(in_val, dict) and 'output' in in_val else str(in_val)
        
        # Call the LLM using the input value
        raw_output = call_llm(prompt=prompt, model="meta.llama3-8b-instruct-v1:0")
        
        # Format the output as JSON
        out_val = {
            "input": prompt,
            "model": "meta.llama3-8b-instruct-v1:0",
            "output": raw_output
        }
        
        self.set_interface(name='output_0', value=out_val)
        st.sidebar.write("### Meta LLama Block Output:")
        st.sidebar.json(out_val)
    else:
        st.sidebar.write("Meta LLama block received no input.")


def invoke_mistral(self):
    """
    Compute function for the Mistral (Model) Block.
    """
    in_val = self.get_interface(name='input_0')
    if in_val:
        st.sidebar.write("Mistral block received input:", in_val)
        
        # Handle input that might be a dictionary or string
        prompt = in_val['output'] if isinstance(in_val, dict) and 'output' in in_val else str(in_val)
        
        # Call the LLM using the input value
        raw_output = call_llm(prompt=prompt, model="mistral.mistral-large-2402-v1:0")
        
        # Format the output as JSON
        out_val = {
            "input": prompt,
            "model": "mistral.mistral-large-2402-v1:0",
            "output": raw_output
        }
        
        self.set_interface(name='output_0', value=out_val)
        st.sidebar.write("### Mistral Block Output:")
        st.sidebar.json(out_val)
    else:
        st.sidebar.write("Mistral block received no input.")


def feed_compute(self):
    """
    Compute function for the Prompt (Feed) Block.
    """
    with st.form("prompt_form"):
        text = st.text_input("Enter Prompt Text:")
        submitted = st.form_submit_button("Submit")
        if submitted:
            st.sidebar.write("Prompt block submitted:", text)
            self.set_interface(name='output_0', value=text)

def final_output_compute(self):
    """
    Compute function for the Final Output Block.
    """
    val = self.get_interface(name='input_0')
    if val:
        st.sidebar.write("Final output block received input:", val)
        st.sidebar.json(val)  # Added JSON display
    else:
        st.sidebar.write("Final output block received no input.")

def web_search_compute(self):
    """
    Compute function for the Web Search (Tool) Block.
    """
    in_val = self.get_interface(name='input_0')
    if in_val:
        st.sidebar.write("Web Search block received input:", in_val)
        
        # Initialize the TavilySearchResults with the API key from secrets
        api_key = st.secrets["TAVILY_API_KEY"]
        search = TavilySearchResults(
            max_results=2, 
            tavily_api_key=api_key
        )
        out_val = search.invoke({"query": str(in_val)})
        
        self.set_interface(name='output_0', value=out_val)
        st.sidebar.write("Web Search block set output:", out_val)
        st.sidebar.json(out_val)  # Display the output in JSON format for better visibility
    else:
        st.sidebar.write("Web Search block received no input.")

def pubmed_search_compute(self):
    """
    Compute function for the PubMed Search (Tool) Block.
    """
    in_val = self.get_interface(name='input_0')
    if in_val:
        st.sidebar.write("PubMed Search block received input:", in_val)
        
        # Use Langchain's PubMedSearchTool
        search_tool = PubmedQueryRun()
        raw_output = search_tool.invoke(in_val)
        
        # Convert the output to a structured JSON format
        out_val = {
            "query": in_val,
            "results": raw_output.split("\n\n")  # Split into separate results
        }
        
        self.set_interface(name='output_0', value=out_val)
        st.sidebar.write("PubMed Search block set output:")
        st.sidebar.json(out_val)  # Now displays properly formatted JSON
    else:
        st.sidebar.write("PubMed Search block received no input.")

def wikipedia_search_compute(self):
    """
    Compute function for the Wikipedia Search (Tool) Block.
    """
    in_val = self.get_interface(name='input_0')
    if in_val:
        st.sidebar.write("Wikipedia Search block received input:", in_val)
        
        # Initialize the WikipediaAPIWrapper and WikipediaQueryRun
        api_wrapper = WikipediaAPIWrapper()
        search_tool = WikipediaQueryRun(api_wrapper=api_wrapper)
        raw_output = search_tool.invoke(in_val)
        
        # Convert the output to a structured JSON format
        out_val = {
            "query": in_val,
            "results": raw_output.split("\n\n")  # Split into separate results
        }
        
        self.set_interface(name='output_0', value=out_val)
        st.sidebar.write("Wikipedia Search block set output:")
        st.sidebar.json(out_val)  # Now displays properly formatted JSON
    else:
        st.sidebar.write("Wikipedia Search block received no input.")

def init_block_compute(self):
    """
    Compute function for the Init Block.
    This block serves as the starting point of the flow.
    """
    st.sidebar.write("Init Block is the start of the flow.")
    
    # Read from session state
    user_input = st.session_state.get("init_input", "")
    
    if user_input:
        self.set_interface(name='output_0', value=user_input)
        st.sidebar.write("Init Block has set the initial value:", user_input)
    else:
        st.sidebar.write("No input provided in Init Block.")


def pack_block_compute(self):
    """
    Compute function for the Pack Block.
    """
    in_val = self.get_interface(name='input_0')
    if in_val:
        st.sidebar.write("Pack Block received input:", in_val)
        # Dummy processing logic
        out_val = f"Packed: {in_val}"
        self.set_interface(name='output_0', value=out_val)
        st.sidebar.write("Pack Block set output:", out_val)
    else:
        st.sidebar.write("Pack Block received no input.")

def combine_block_compute(self):
    """
    Compute function for the Combine Block.
    """
    # Collect inputs
    inputs = [
        self.get_interface(name='input_1'),
        self.get_interface(name='input_2'),
        self.get_interface(name='input_3')
    ]
    
    # Debug: Print input values
    st.sidebar.write("Combine Block inputs:", inputs)
    
    # Filter out None values and join the inputs
    combined_val = " + ".join(filter(None, inputs))
    
    if combined_val:
        st.sidebar.write("Combine Block received inputs:", inputs)
        self.set_interface(name='output_0', value=combined_val)
        st.sidebar.write("Combine Block set output:", combined_val)
        st.sidebar.json(combined_val)  # Added JSON display
    else:
        st.sidebar.write("Combine Block received no valid inputs.")

###############################################################################
# 2. Utility Functions
###############################################################################

def parse_template_variables(prompt_template: str):
    """
    Parses the prompt template and extracts all variables enclosed in curly braces.
    """
    return re.findall(r'\{(.*?)\}', prompt_template)

###############################################################################
# 3. Define the Main Page with Barfi Blocks
###############################################################################

def main_page():
    """
    Renders the main Barfi blocks page.
    Includes the Init Block as the starting point of the flow.
    Creates one Prompt block per template (instead of one global block).
    """
    st.sidebar.title("Barfi")
    
    # Check login status
    login_status = st.session_state.get("logged_in", False)
    
    # Display Pack Block availability info with more visibility
    if login_status:
        st.sidebar.success("✅ Pack Block is AVAILABLE - You are logged in!")
    else:
        st.sidebar.warning("⚠️ Pack Block is UNAVAILABLE - Login required")
        st.sidebar.info("Login using the Authentication section below to access the Pack Block")

    # Use a single stable key so Barfi reuses the same canvas across re-runs
    if "barfi_key" not in st.session_state:
        st.session_state["barfi_key"] = "barfi_default"

    reset_canvas = st.sidebar.button("Reset Canvas")
    if reset_canvas:
        # If clicked, set a new key so Barfi resets the layout
        st.session_state["barfi_key"] = "barfi_reset"
        st.rerun()

    # Show a dropdown of all saved templates, if any
    template_names = []
    if "templates" in st.session_state and st.session_state["templates"]:
        template_names = list(st.session_state["templates"].keys())

    selected_template = st.sidebar.selectbox(
        "Select a saved template:",
        template_names if template_names else ["No saved templates"]
    )
    if selected_template and selected_template != "No saved templates":
        st.sidebar.write("You selected:", selected_template)
        st.sidebar.json(st.session_state["templates"][selected_template])

    # Optional: Prompt for initialization
    st.sidebar.write("Initialize Flow")
    st.sidebar.text_input("Enter your prompt here", key="init_input")

    # -----------------------------------------------------------------
    # Create the standard blocks: Final Output, Anthropic, Web Search, etc.
    # -----------------------------------------------------------------
    final_output = Block(name="Final Output")
    final_output.add_input(name='input_0')
    final_output.add_compute(final_output_compute)

    anthropic_block = Block(name='Anthropic (Model)')
    anthropic_block.add_input(name='input_0')
    anthropic_block.add_output(name='output_0')
    anthropic_block.add_compute(invoke_anthropic)

    titan_block = Block(name='Titan (Model)')
    titan_block.add_input(name='input_0')
    titan_block.add_output(name='output_0')
    titan_block.add_compute(invoke_titan)

    llama_block = Block(name='Meta (Model)')
    llama_block.add_input(name='input_0')
    llama_block.add_output(name='output_0')
    llama_block.add_compute(invoke_meta_llama)

    mistral_block = Block(name='Mistral (Model)')
    mistral_block.add_input(name='input_0')
    mistral_block.add_output(name='output_0')
    mistral_block.add_compute(invoke_mistral)

    web_search_block = Block(name='Web Search (Tool)')
    web_search_block.add_input(name='input_0')
    web_search_block.add_output(name='output_0')
    web_search_block.add_compute(web_search_compute)

    init_block = Block(name="Init Block")
    init_block.add_output(name="output_0")
    init_block.add_compute(init_block_compute)

    pubmed_block = Block(name='PubMed Search (Tool)')
    pubmed_block.add_input(name='input_0')
    pubmed_block.add_output(name='output_0')
    pubmed_block.add_compute(pubmed_search_compute)

    wikipedia_block = Block(name='Wikipedia Search (Tool)')
    wikipedia_block.add_input(name='input_0')
    wikipedia_block.add_output(name='output_0')
    wikipedia_block.add_compute(wikipedia_search_compute)

    combine_block = Block(name='Combine Block')
    combine_block.add_input(name='input_1')
    combine_block.add_input(name='input_2')
    combine_block.add_input(name='input_3')
    combine_block.add_output(name='output_0')
    combine_block.add_compute(combine_block_compute)

    # -----------------------------------------------------------------
    # Create base blocks list - all blocks except Pack Block which is conditional
    # -----------------------------------------------------------------
    base_blocks = [
        init_block,
        anthropic_block,
        web_search_block,
        pubmed_block,
        wikipedia_block,
        final_output,
        combine_block,
        titan_block,
        llama_block,
        mistral_block
    ]
    
    # Conditionally add Pack Block if user is logged in
    if login_status:
        # Create Pack Block only when logged in
        pack_block = Block(name='Pack Block')
        pack_block.add_input(name='input_0')
        pack_block.add_output(name='output_0')
        pack_block.add_compute(pack_block_compute)
        
        # Add to base blocks
        base_blocks.append(pack_block)
    
    # ------------------------------------------------
    # Create a Prompt block PER template in session_state
    # ------------------------------------------------
    if "templates" in st.session_state and st.session_state["templates"]:
        for tmpl_name, tmpl_data in st.session_state["templates"].items():
            prompt_template = tmpl_data["prompt_template"]
            variables = parse_template_variables(prompt_template)

            block_title = f"Prompt: {tmpl_name}"
            new_block = Block(name=block_title)

            for var in variables:
                new_block.add_input(name=var)

            new_block.add_output(name='output_0')
            new_block.add_compute(prompt_compute_factory(prompt_template, variables))

            base_blocks.append(new_block)

    # -----------------------------------------------------------------
    # Render everything in Barfi, with our stable key
    # -----------------------------------------------------------------
    st_barfi(
        base_blocks=base_blocks,
        key=st.session_state["barfi_key"]
    )

###############################################################################
# 4. Compute Function Factory for Prompt Block
###############################################################################

def prompt_compute_factory(prompt_template: str, variables: list):
    """
    Creates a compute function for the Prompt Block based on the template and variables.
    """
    def prompt_compute(self):
        # Collect inputs for each variable
        input_values = {}
        for var in variables:
            input_val = self.get_interface(name=var)
            if input_val:
                input_values[var] = input_val
            else:
                st.error(f"Missing input for variable: {var}")
                return  # Exit if any input is missing

        # Inject variables into the prompt template
        try:
            final_prompt = prompt_template.format(**input_values)
            st.sidebar.write("### Final Prompt:")
            st.sidebar.code(final_prompt, language="markdown")

            # Set the output interface with the formatted prompt
            self.set_interface(name='output_0', value=final_prompt)

        except Exception as e:
            st.error(f"Error generating prompt: {e}")

    return prompt_compute


###############################################################################
# 6. Page Navigation
###############################################################################

def main():
    """
    Manages page navigation between the main page and the prompt templates page.
    """
    # Set default page if not already set
    if "page" not in st.session_state:
        st.session_state["page"] = "home"
    
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
            with st.form(key="persistent_login_form"):
                username = st.text_input("Username or Email", key="login_username")
                password = st.text_input("Password", type="password", key="login_password")
                login_submit = st.form_submit_button("Log In")
                
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
            # Show user info and logout button
            user_info = f"**User:** {st.session_state.get('username', 'User')}"
            if st.session_state.get("premium_status", False):
                user_info += " ⭐ Premium"
            st.write(user_info)
            
            if st.button("🚪 Logout", key="main_logout_btn", use_container_width=True):
                # Use the updated logout function
                logout()
                st.success("Logged out successfully")
                st.rerun()
        
        st.write("---")
    
    # Sidebar button to switch to Prompt Templates page
    if st.sidebar.button("Prompt Templates", use_container_width=True):
        st.session_state["page"] = "prompt_templates"
        st.rerun()

    # Debugging - uncomment if needed
    # st.sidebar.write(f"Current page: {st.session_state['page']}")
    
    # Display the appropriate page based on session state
    if st.session_state["page"] == "prompt_templates":
        prompt_templates_app()
    else:
        main_page()

###############################################################################
# 7. Entry Point
###############################################################################

if __name__ == "__main__":
    # Create session state variables if they don't exist
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'username' not in st.session_state:
        st.session_state.username = None
    if 'access_token' not in st.session_state:
        st.session_state.access_token = None
        
    # Display the main app
    main()