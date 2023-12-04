from agency_swarm import BaseTool
from agency_swarm.util import get_openai_client
from pydantic import Field


class GenerateProposal(BaseTool):
    """Generate a proposal for a project based on a project brief.
    Remember that user does not have access to the output of this function.
    You must send it back to him after execution."""

    project_brief: str = Field(..., description="The project brief to generate a proposal for.")

    def run(self):
        client = get_openai_client()
        completion = client.chat.completions.create(
            model="gpt-4-1106-preview",
            messages=[
                {
                    "role": "system",
                    "content": "You are a professional proposal drafting assistant. "
                    "Do not include any actual technologies or technical details into proposal until "
                    "specified in the project brief. Be short.",
                },
                {
                    "role": "user",
                    "content": "Please draft a proposal for the following project brief: " + self.project_brief,
                },
            ],
        )

        return str(completion.choices[0].message.content)
