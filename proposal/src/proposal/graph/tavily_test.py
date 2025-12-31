from dotenv import load_dotenv

load_dotenv()

from langchain_community.tools.tavily_search import TavilySearchResults

tavily = TavilySearchResults(
    max_results=5,
    search_depth="advanced",
    include_raw_content=True,
)

query = 'banking consulting proposal systems integration executive summary pdf'

results = tavily.invoke({"query": query})

import pdb;pdb.set_trace();
for i, r in enumerate(results, start=1):
    print(f"--- Result {i} ---")
    print("Title:", r.get("title"))
    print("URL:", r.get("url"))
    print("Content Preview:\n", r.get("content", "")[:500])
    print("\n")