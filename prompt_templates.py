import streamlit as st
import json
from llm import call_llm


def prompt_templates_app():
    """
    Renders the Prompt Templates UI.
    """

    # 1. Back button to go to main page
    if st.sidebar.button("Back to Main App"):
        st.session_state["page"] = "home"
        st.rerun()

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
