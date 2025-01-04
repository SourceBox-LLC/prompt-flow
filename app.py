# app.py

import streamlit as st
from barfi import st_barfi, Block
from prompt_templates import prompt_templates_app

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
        out_val = f"Anthropic response: {in_val}"
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

def tavily_search_compute(self):
    """
    Compute function for the Tavily Search (Tool) Block.
    """
    in_val = self.get_interface(name='input_0')
    if in_val:
        st.sidebar.write("Tavily Search block received input:", in_val)
        out_val = f"Tavily Search result for: {in_val}"
        self.set_interface(name='output_0', value=out_val)
        st.sidebar.write("Tavily Search block set output:", out_val)
    else:
        st.sidebar.write("Tavily Search block received no input.")

def duckduckgo_search_compute(self):
    """
    Compute function for the DuckDuckGo Search (Tool) Block.
    """
    in_val = self.get_interface(name='input_0')
    if in_val:
        st.sidebar.write("DuckDuckGo Search block received input:", in_val)
        out_val = f"DuckDuckGo Search result for: {in_val}"
        self.set_interface(name='output_0', value=out_val)
        st.sidebar.write("DuckDuckGo Search block set output:", out_val)
    else:
        st.sidebar.write("DuckDuckGo Search block received no input.")

def init_block_compute(self):
    """
    Compute function for the Init Block.
    This block serves as the starting point of the flow.
    """
    st.sidebar.write("Init Block is the start of the flow.")
    # Optionally, you can set an initial value or perform any startup logic here.
    initial_value = "Flow Initiated"
    self.set_interface(name='output_0', value=initial_value)
    st.sidebar.write("Init Block has set the initial value.")

###############################################################################
# 2. Define the Main Page with Barfi Blocks
###############################################################################

def main_page():
    """
    Renders the main Barfi blocks page.
    Includes the Init Block as the starting point of the flow.
    """
    st.sidebar.title("Barfi")

    # Dynamically load template names from session_state
    template_names = []
    if "templates" in st.session_state and st.session_state["templates"]:
        template_names = list(st.session_state["templates"].keys())

    # Display a selectbox of all saved templates
    selected_template = st.sidebar.selectbox(
        "Select a saved template:",
        template_names if template_names else ["No saved templates"]
    )

    if selected_template and selected_template != "No saved templates":
        st.sidebar.write("You selected:", selected_template)
        # Optionally show data about the selected template
        st.sidebar.json(st.session_state["templates"][selected_template])

    # 1. Create the Init Block
    init_block = Block(name="Init Block")
    # No inputs, only an output
    init_block.add_output(name="output_0")
    init_block.add_compute(init_block_compute)

    # 2. Create the existing blocks
    feed = Block(name='Prompt')
    feed.add_output(name='output_0')
    feed.add_compute(feed_compute)

    final_output = Block(name="Final Output")
    final_output.add_input(name='input_0')
    final_output.add_compute(final_output_compute)

    anthropic_block = Block(name='Anthropic (Model)')
    anthropic_block.add_input(name='input_0')
    anthropic_block.add_output(name='output_0')
    anthropic_block.add_compute(invoke_anthropic)

    tavily_block = Block(name='Tavily Search (Tool)')
    tavily_block.add_input(name='input_0')
    tavily_block.add_output(name='output_0')
    tavily_block.add_compute(tavily_search_compute)

    duckduckgo_block = Block(name='DuckDuckGo Search (Tool)')
    duckduckgo_block.add_input(name='input_0')
    duckduckgo_block.add_output(name='output_0')
    duckduckgo_block.add_compute(duckduckgo_search_compute)

    # 3. Render the Barfi interface with all blocks including Init Block
    st_barfi(
        base_blocks=[
            init_block,          # Init Block as the starting point
            feed,
            anthropic_block,
            tavily_block,
            duckduckgo_block,
            final_output
        ]
    )

###############################################################################
# 3. Page Navigation
###############################################################################

def main():
    """
    Manages page navigation between the main page and the prompt templates page.
    """
    # Initialize session state
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
# 4. Entry Point
###############################################################################

if __name__ == "__main__":
    main()
