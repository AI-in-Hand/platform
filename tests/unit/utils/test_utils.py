from unittest.mock import MagicMock, patch

from nalgonda.utils import (
    chunk_input_with_token_limit,
    get_chat_completion,
    get_token_count,
    tokenize,
    truncate_oversized_chunk,
)


def test_get_chat_completion():
    mock_completion = MagicMock()
    mock_completion.choices = [MagicMock()]
    mock_completion.choices[0].message.content = "test response"

    with patch("nalgonda.utils.get_openai_client") as mock_client:
        mock_client.return_value.chat.completions.create.return_value = mock_completion
        response = get_chat_completion("system message", "user prompt", "text-davinci-003")
        assert response == "test response"


@patch("nalgonda.utils.tiktoken.get_encoding")
def test_tokenize(mock_get_encoding):
    mock_get_encoding.return_value.encode.return_value = [1, 2, 3]
    tokens = tokenize("sample text")
    assert tokens == [1, 2, 3]


@patch("nalgonda.utils.tokenize")
def test_get_token_count(mock_tokenize):
    mock_tokenize.return_value = [1, 2, 3]
    count = get_token_count("sample text")
    assert count == 3


@patch("nalgonda.utils.get_token_count")
def test_chunk_input_with_token_limit_within_limit(mock_get_token_count):
    mock_get_token_count.side_effect = lambda text: len(text)  # Simplified token count
    chunks = chunk_input_with_token_limit("This is a test.", 10, " ")
    assert chunks == ["This is a ", "test. "]


@patch("nalgonda.utils.tokenize")
@patch("nalgonda.utils.tiktoken.get_encoding")
def test_truncate_oversized_chunk(mock_get_encoding, mock_tokenize):
    mock_tokenize.side_effect = lambda text: list(range(len(text)))  # Fake tokens
    mock_get_encoding.return_value.decode.return_value = "truncated"
    truncated = truncate_oversized_chunk("This is way too long.", 5, " ")
    assert truncated == "truncated "
