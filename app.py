# app.py

import streamlit as st
from barfi import st_barfi, Block
from prompt_templates import prompt_templates_app  # <-- Import your function

###############################################################################
# 1. Define your Barfi blocks (Main Page Content)
###############################################################################
def invoke_anthropic(self):
    in_val = self.get_interface(name='input_0')
    if in_val:
        st.sidebar.write("Anthropic block received input:", in_val)
        out_val = f"Anthropic response: {in_val}"
        self.set_interface(name='output_0', value=out_val)
        st.sidebar.write("Anthropic block set output:", out_val)
    else:
        st.sidebar.write("Anthropic block received no input.")

def feed_compute(self):
    with st.form("prompt_form"):
        text = st.text_input("Enter Prompt Text:")
        submitted = st.form_submit_button("Submit")
        if submitted:
            st.sidebar.write("Prompt block submitted:", text)
            self.set_interface(name='output_0', value=text)

def final_output_compute(self):
    val = self.get_interface(name='input_0')
    if val:
        st.sidebar.write("Final output block received input:", val)
    else:
        st.sidebar.write("Final output block received no input.")

def tavily_search_compute(self):
    in_val = self.get_interface(name='input_0')
    if in_val:
        st.sidebar.write("Tavily Search block received input:", in_val)
        out_val = f"Tavily Search result for: {in_val}"
        self.set_interface(name='output_0', value=out_val)
        st.sidebar.write("Tavily Search block set output:", out_val)
    else:
        st.sidebar.write("Tavily Search block received no input.")

def duckduckgo_search_compute(self):
    in_val = self.get_interface(name='input_0')
    if in_val:
        st.sidebar.write("DuckDuckGo Search block received input:", in_val)
        out_val = f"DuckDuckGo Search result for: {in_val}"
        self.set_interface(name='output_0', value=out_val)
        st.sidebar.write("DuckDuckGo Search block set output:", out_val)
    else:
        st.sidebar.write("DuckDuckGo Search block received no input.")

def main_page():
    """
    This function renders your main Barfi blocks page.
    """
    st.sidebar.title("Barfi")

    # base blocks
    feed = Block(name='Prompt')
    feed.add_output(name='output_0')
    feed.add_compute(feed_compute)

    final_output = Block(name="Final Output")
    final_output.add_input(name='input_0')
    final_output.add_compute(final_output_compute)

    # Model Blocks
    anthropic_block = Block(name='Anthropic (Model)')
    anthropic_block.add_input(name='input_0')
    anthropic_block.add_output(name='output_0')
    anthropic_block.add_compute(invoke_anthropic)

    # Tool Blocks
    tavily_block = Block(name='Tavily Search (Tool)')
    tavily_block.add_input(name='input_0')
    tavily_block.add_output(name='output_0')
    tavily_block.add_compute(tavily_search_compute)

    duckduckgo_block = Block(name='DuckDuckGo Search (Tool)')
    duckduckgo_block.add_input(name='input_0')
    duckduckgo_block.add_output(name='output_0')
    duckduckgo_block.add_compute(duckduckgo_search_compute)

    # Render the Barfi interface
    st_barfi(base_blocks=[
        feed,
        anthropic_block,
        tavily_block,
        duckduckgo_block,
        final_output
    ])

###############################################################################
# 2. Page Navigation
###############################################################################
def main():
    # Initialize session state
    if "page" not in st.session_state:
        st.session_state["page"] = "home"

    # Sidebar button to switch pages
    if st.sidebar.button("Prompt Templates"):
        st.session_state["page"] = "prompt_templates"
        st.rerun()

    # Display either the main page or the prompt templates page
    if st.session_state["page"] == "prompt_templates":
        prompt_templates_app()  # From prompt_templates.py
    else:
        main_page()


if __name__ == "__main__":
    main()
