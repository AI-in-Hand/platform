from agency_swarm import Agency
from agency_swarm.messages import MessageOutput

from backend.services.context_vars_manager import ContextEnvVarsManager


def get_next_response(agency: Agency, user_message: str, user_id: str, agency_id: str) -> MessageOutput | None:
    try:
        # Set the user_id and agency_id in the context variables
        ContextEnvVarsManager.set("user_id", user_id)
        ContextEnvVarsManager.set("agency_id", agency_id)
        response_generator = agency.get_completion(message=user_message, yield_messages=True)
        return next(response_generator)
    except StopIteration:
        return None
