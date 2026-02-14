from langchain_tavily import TavilySearch  # updated 1.0
from langchain_community.document_loaders import WikipediaLoader

tavily_search = TavilySearch(max_results=3)
