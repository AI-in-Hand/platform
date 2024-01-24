from agency_swarm.tools import BaseTool
from duckduckgo_search import DDGS
from pydantic import Field


class SearchWeb(BaseTool):
    """Search the web with a search phrase and return the results."""

    phrase: str = Field(
        ...,
        description="The search phrase you want to use. Optimize the search phrase for an internet search engine.",
    )
    max_results: int = Field(default=10, description="The maximum number of search results to return, default is 10.")

    def run(self) -> str:
        with DDGS() as ddgs:
            return "\n".join(str(result) for result in ddgs.text(self.phrase, max_results=self.max_results))
