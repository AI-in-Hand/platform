from agency_swarm.util import get_openai_client


def get_chat_completion(user_prompt, system_message, **kwargs) -> str:
    """Generate a chat completion based on a prompt and a system message.
    This function is a wrapper around the OpenAI API.
    """
    from base_agency.config import settings

    client = get_openai_client()
    completion = client.chat.completions.create(
        model=settings.gpt_model,
        messages=[
            {
                "role": "system",
                "content": system_message,
            },
            {
                "role": "user",
                "content": user_prompt,
            },
        ],
        **kwargs,
    )

    return str(completion.choices[0].message.content)
