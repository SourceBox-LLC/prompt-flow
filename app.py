import streamlit as st
from barfi import st_barfi, Block
from prompt_templates import prompt_templates_app
import re  # For parsing variables from the prompt template
from langchain_community.tools.pubmed.tool import PubmedQueryRun
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper
import boto3
import json
from langchain_community.tools.tavily_search import TavilySearchResults

# --- NEW IMPORT for ChatBedrock-based call_llm ---
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
        
        # Call the LLM using the input value
        out_val = call_llm(prompt=in_val)
        
        self.set_interface(name='output_0', value=out_val)
        st.sidebar.write("Anthropic block set output:", out_val)
    else:
        st.sidebar.write("Anthropic block received no input.")

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
        out_val = search_tool.invoke(in_val)
        
        self.set_interface(name='output_0', value=out_val)
        st.sidebar.write("PubMed Search block set output:", out_val)
        st.sidebar.json(out_val)  # Display the output in JSON format for better visibility
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
        out_val = search_tool.invoke(in_val)
        
        self.set_interface(name='output_0', value=out_val)
        st.sidebar.write("Wikipedia Search block set output:", out_val)
        st.sidebar.json(out_val)  # Display the output in JSON format for better visibility
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

def parser_block_compute(self):
    """
    Compute function for the Parser Block.
    """
    selected_options = st.multiselect(
        "Select parsing options:",
        options=["{}", "[]", "<>", "()", "''", '""'],
        default=["{}"]
    )
    st.sidebar.write("Selected parsing options:", selected_options)
    
    # Input
    in_val = self.get_interface(name='input_0')
    if not in_val:
        st.sidebar.write("No input to parse.")
        for node in ['curly', 'square', 'angle', 'paren', 'single_quote', 'double_quote']:
            self.set_interface(name=node, value=None)
        return

    # For each bracket type, either produce a 'parsed' output or None
    if "{}" in selected_options:
        self.set_interface(name='curly', value=f"Parsed Curly: {in_val}")
    else:
        self.set_interface(name='curly', value=None)

    if "[]" in selected_options:
        self.set_interface(name='square', value=f"Parsed Square: {in_val}")
    else:
        self.set_interface(name='square', value=None)

    if "<>" in selected_options:
        self.set_interface(name='angle', value=f"Parsed Angle: {in_val}")
    else:
        self.set_interface(name='angle', value=None)

    if "()" in selected_options:
        self.set_interface(name='paren', value=f"Parsed Paren: {in_val}")
    else:
        self.set_interface(name='paren', value=None)

    if "''" in selected_options:
        self.set_interface(name='single_quote', value=f"Parsed Single Quotes: {in_val}")
    else:
        self.set_interface(name='single_quote', value=None)

    if '""' in selected_options:
        self.set_interface(name='double_quote', value=f"Parsed Double Quotes: {in_val}")
    else:
        self.set_interface(name='double_quote', value=None)

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

    web_search_block = Block(name='Web Search (Tool)')
    web_search_block.add_input(name='input_0')
    web_search_block.add_output(name='output_0')
    web_search_block.add_compute(web_search_compute)

    init_block = Block(name="Init Block")
    init_block.add_output(name="output_0")
    init_block.add_compute(init_block_compute)

    parser_block = Block(name="Parser Block")
    parser_block.add_input(name='input_0')
    parser_block.add_output(name='curly {}')
    parser_block.add_output(name='square []')
    parser_block.add_output(name='angle <>')
    parser_block.add_output(name='paren ()')
    parser_block.add_output(name='single_quote \'\'')
    parser_block.add_output(name='double_quote \"\"')
    parser_block.add_compute(parser_block_compute)

    pubmed_block = Block(name='PubMed Search (Tool)')
    pubmed_block.add_input(name='input_0')
    pubmed_block.add_output(name='output_0')
    pubmed_block.add_compute(pubmed_search_compute)

    wikipedia_block = Block(name='Wikipedia Search (Tool)')
    wikipedia_block.add_input(name='input_0')
    wikipedia_block.add_output(name='output_0')
    wikipedia_block.add_compute(wikipedia_search_compute)

    pack_block = Block(name='Pack Block')
    pack_block.add_input(name='input_0')
    pack_block.add_output(name='output_0')
    pack_block.add_compute(pack_block_compute)

    combine_block = Block(name='Combine Block')
    combine_block.add_input(name='input_1')
    combine_block.add_input(name='input_2')
    combine_block.add_input(name='input_3')
    combine_block.add_output(name='output_0')
    combine_block.add_compute(combine_block_compute)

    # ------------------------------------------------
    # Create a Prompt block PER template in session_state
    # ------------------------------------------------
    all_prompt_blocks = []
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

            all_prompt_blocks.append(new_block)

    # -----------------------------------------------------------------
    # Render everything in Barfi, with our stable key
    # -----------------------------------------------------------------
    st_barfi(
        base_blocks=[
            parser_block,
            init_block,
            anthropic_block,
            web_search_block,
            pubmed_block,
            wikipedia_block,
            final_output,
            pack_block,
            combine_block,
            *all_prompt_blocks
        ],
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
    if "page" not in st.session_state:
        st.session_state["page"] = "home"

    # Sidebar button to switch to Prompt Templates page
    if st.sidebar.button("Prompt Templates"):
        st.session_state["page"] = "prompt_templates"
        st.rerun()

    # Display the appropriate page based on session state
    if st.session_state["page"] == "prompt_templates":
        prompt_templates_app()
    else:
        main_page()

###############################################################################
# 7. Entry Point
###############################################################################

if __name__ == "__main__":
    main()
