from agency_swarm.tools import BaseTool
from duckduckgo_search import DDGS
from pydantic import Field


class SearchWeb(BaseTool):
    """Search the web with a search phrase and return the results."""

    phrase: str = Field(
        ...,
        description="The search phrase you want to use. " "Optimize the search phrase for an internet search engine.",
    )

    # This code will be executed if the agent calls this tool
    def run(self):
        with DDGS() as ddgs:
            return str(r for r in ddgs.text(self.phrase, max_results=3))
