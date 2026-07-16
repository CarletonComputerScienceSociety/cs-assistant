from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from src.config import settings
from src.infrastructure import llm


def mock_async_client(json_data=None, raise_for_status_side_effect=None):
    response = MagicMock()
    response.json.return_value = json_data or {}
    response.raise_for_status.side_effect = raise_for_status_side_effect

    client = AsyncMock()
    client.post = AsyncMock(return_value=response)

    patcher = patch("src.infrastructure.llm.httpx.AsyncClient")
    mocked_async_client_cls = patcher.start()

    mocked_context_manager = AsyncMock()
    mocked_context_manager.__aenter__.return_value = client
    mocked_context_manager.__aexit__.return_value = None

    mocked_async_client_cls.return_value = mocked_context_manager

    return patcher, client, response


def test_embed_document_prefix_value_is_pinned():
    assert llm.EMBED_DOCUMENT_PREFIX == "search_document: "


async def test_embed_uses_query_prefix_and_embedding_model():
    fake_embedding = [0.0] * settings.embedding_dim
    patcher, client, _ = mock_async_client(json_data={"embedding": fake_embedding})

    try:
        result = await llm.embed("hello", is_query=True)

        assert result == fake_embedding
        args, kwargs = client.post.call_args

        assert args[0].endswith("/api/embeddings")
        assert kwargs["json"]["model"] == settings.ollama_embedding_model
        assert kwargs["json"]["prompt"] == f"{llm.EMBED_QUERY_PREFIX}hello"
    finally:
        patcher.stop()


async def test_embed_uses_document_prefix():
    fake_embedding = [0.0] * settings.embedding_dim
    patcher, client, _ = mock_async_client(json_data={"embedding": fake_embedding})

    try:
        await llm.embed("hello", is_query=False)

        _, kwargs = client.post.call_args
        assert kwargs["json"]["prompt"] == f"{llm.EMBED_DOCUMENT_PREFIX}hello"
    finally:
        patcher.stop()


async def test_embed_raises_value_error_on_dimension_mismatch():
    wrong_embedding = [0.0] * (settings.embedding_dim - 1)
    patcher, _, _ = mock_async_client(json_data={"embedding": wrong_embedding})

    try:
        with pytest.raises(ValueError, match="mismatch"):
            await llm.embed("hello", is_query=True)
    finally:
        patcher.stop()


async def test_chat_uses_chat_model_and_returns_message_content():
    patcher, client, _ = mock_async_client(json_data={"message": {"content": "hi back"}})

    messages = [{"role": "user", "content": "hello"}]

    try:
        result = await llm.chat(messages)

        assert result == "hi back"
        args, kwargs = client.post.call_args

        assert args[0].endswith("/api/chat")
        assert kwargs["json"]["model"] == settings.ollama_chat_model
        assert kwargs["json"]["messages"] == messages
        assert kwargs["json"]["stream"] is False
    finally:
        patcher.stop()


async def test_http_errors_propagate_for_embed_and_chat():
    request = httpx.Request("POST", "http://test/api")
    response = httpx.Response(500, request=request)
    error = httpx.HTTPStatusError("boom", request=request, response=response)

    patcher, _, _ = mock_async_client(
        json_data={},
        raise_for_status_side_effect=error,
    )

    try:
        with pytest.raises(httpx.HTTPStatusError):
            await llm.embed("hello", is_query=True)

        with pytest.raises(httpx.HTTPStatusError):
            await llm.chat([{"role": "user", "content": "hello"}])
    finally:
        patcher.stop()
