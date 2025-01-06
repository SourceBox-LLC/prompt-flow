from langchain_community.tools.tavily_search import TavilySearchResults
import streamlit as st

def test_tavily_search():
    # Example input for testing
    test_input = "Example search query"

    # Initialize the TavilySearchResults with the API key from secrets
    api_key = st.secrets["TAVILY_API_KEY"]
    search = TavilySearchResults(
        max_results=2, 
        tavily_api_key=api_key
    )

    # Invoke the search with the test input
    try:
        result = search.invoke({"query": test_input})
        print("Tavily Search Result:", result)
    except Exception as e:
        print(f"Error during Tavily Search: {e}")

# Run the test function
if __name__ == "__main__":
    test_tavily_search()
