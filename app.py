import streamlit as st
from barfi import st_barfi, Block
from prompt_templates import prompt_templates_app
import re  # For parsing variables from the prompt template

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
# 2. Utility Functions
###############################################################################

def parse_template_variables(prompt_template: str):
    """
    Parses the prompt template and extracts all variables enclosed in curly braces.

    Args:
        prompt_template (str): The prompt template containing placeholders.

    Returns:
        List[str]: A list of variable names.
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

    if "barfi_key" not in st.session_state:
        st.session_state["barfi_key"] = "barfi_default"
    
    reset_canvas = st.sidebar.button("Reset Canvas")
    if reset_canvas:
        # Flip to a new key so that Barfi doesn't load old state
        st.session_state["barfi_key"] = "barfi_reset"
        st.rerun()

    # (Optional) You can still show a dropdown of all saved templates in the sidebar
    # for informational purposes, but it will NOT affect the block creation below.
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

    # ---------------------------
    # Create Other Existing Blocks
    # ---------------------------
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

    init_block = Block(name="Init Block")
    init_block.add_output(name="output_0")
    init_block.add_compute(init_block_compute)

    # ------------------------------------------------
    # Create a Prompt block PER template in session_state
    # ------------------------------------------------
    all_prompt_blocks = []
    if "templates" in st.session_state and st.session_state["templates"]:
        for tmpl_name, tmpl_data in st.session_state["templates"].items():
            prompt_template = tmpl_data["prompt_template"]
            variables = parse_template_variables(prompt_template)

            # Give each template a unique name, so they show up distinctly in the Barfi menu
            block_title = f"Prompt: {tmpl_name}"
            new_block = Block(name=block_title)

            # Add input nodes for each variable
            for var in variables:
                new_block.add_input(name=var)

            # Add a single output node
            new_block.add_output(name='output_0')

            # Assign the compute function
            new_block.add_compute(prompt_compute_factory(prompt_template, variables))

            all_prompt_blocks.append(new_block)

    # -----------------------------
    # Render Everything in Barfi
    # -----------------------------
    st_barfi(
        base_blocks=[
            init_block,
            anthropic_block,
            tavily_block,
            duckduckgo_block,
            final_output,
            *all_prompt_blocks  # add all generated prompt blocks
        ],
        key=st.session_state["barfi_key"]
    )

###############################################################################
# 4. Compute Function Factory for Prompt Block
###############################################################################

def prompt_compute_factory(prompt_template: str, variables: list):
    """
    Creates a compute function for the Prompt Block based on the template and variables.

    Args:
        prompt_template (str): The prompt template with placeholders.
        variables (list): List of variable names to inject into the prompt.

    Returns:
        function: A compute function tailored for the Prompt Block.
    """
    def prompt_compute(self):
        """
        Compute function for the dynamic Prompt Block.
        It collects inputs for each variable and generates the final prompt.
        """
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

            # Call the LLM (assuming call_llm is accessible here)
            output = call_llm(
                prompt=final_prompt,
                model=st.session_state.get("current_model", "cohere.command-r-plus-v1:0"),
                temperature=st.session_state.get("current_temperature", 0.7)
            )

            st.sidebar.write("### Model Output:")
            st.sidebar.write(output)

            # Set the output interface
            self.set_interface(name='output_0', value=output)

        except Exception as e:
            st.error(f"Error generating prompt: {e}")

    return prompt_compute

###############################################################################
# 5. Define the Call LLM Function
###############################################################################

def call_llm(prompt: str, model="cohere.command-r-plus-v1:0", temperature=0.7) -> str:
    """
    Example LLM call using AWS Bedrock's Cohere model: cohere.command-r-plus-v1:0.
    Adjust the JSON structure based on the actual model's response in your environment.
    """
    bedrock = boto3.client("bedrock-runtime", region_name="us-east-1")
    try:
        body = {
            "prompt": prompt,
            "temperature": temperature,
        }

        response = bedrock.invoke_model(
            modelId=model,
            contentType="application/json",
            accept="application/json",
            body=json.dumps(body),
        )

        response_body = response["body"].read()
        result = json.loads(response_body)

        # Adapt if the response structure changes
        if "completions" in result and len(result["completions"]) > 0:
            generated_text = result["completions"][0]["data"]["text"]
        else:
            generated_text = "No output from model."

        return generated_text.strip()

    except Exception as e:
        return f"Error calling Bedrock model: {e}"

###############################################################################
# 6. Page Navigation
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
# 7. Entry Point
###############################################################################

if __name__ == "__main__":
    main()
