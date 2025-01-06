from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper

def test_wikipedia_search():
    # Create an instance of the WikipediaAPIWrapper
    api_wrapper = WikipediaAPIWrapper()
    
    # Create an instance of the WikipediaQueryRun tool with the API wrapper
    search_tool = WikipediaQueryRun(api_wrapper=api_wrapper)
    
    # Define a test query
    test_query = "Python programming language"
    
    # Invoke the search tool with the test query
    result = search_tool.invoke(test_query)
    
    # Print the result
    print("Wikipedia Search Result for '{}':".format(test_query))
    print(result)

# Run the test
if __name__ == "__main__":
    test_wikipedia_search()
