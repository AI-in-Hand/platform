from collections.abc import Generator

from agency_swarm.messages import MessageOutput

from backend.services.context_vars_manager import ContextEnvVarsManager


def get_next_response(
    response_generator: Generator[MessageOutput, None, None], user_id: str, agency_id: str
) -> MessageOutput | None:
    try:
        # Set the user_id and agency_id in the context variables
        ContextEnvVarsManager.set("user_id", user_id)
        ContextEnvVarsManager.set("agency_id", agency_id)
        return next(response_generator)
    except StopIteration:
        return None
