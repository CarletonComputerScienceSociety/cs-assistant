from unittest.mock import AsyncMock, MagicMock, patch
from src.retrieval.services.retrieval_service import (
    get_relevant_chunks,
    Repository,
    settings,
)


@patch("src.retrieval.services.retrieval_service.async_session_factory")
@patch.object(Repository, "top_k_chunks", new_callable=AsyncMock)
@patch("src.retrieval.services.embedding_service.embed_query", new_callable=AsyncMock)
async def test_get_relevant_chunks(
    mock_embed_query, mock_top_k_chunks, mock_async_session_factory
):
    fake_embedding = [0.1, 0.2, 0.3]
    mock_embed_query.return_value = fake_embedding
    sentinel_result = ["sentinel_chunk_1", "sentinel_chunk_2"]
    mock_top_k_chunks.return_value = sentinel_result
    mock_session = MagicMock()
    mock_ctx = AsyncMock()
    mock_ctx.__aenter__.return_value = mock_session
    mock_async_session_factory.return_value = mock_ctx
    question = "What is the meaning of life?"
    result = await get_relevant_chunks(question)
    mock_embed_query.assert_awaited_once_with(question)
    mock_top_k_chunks.assert_awaited_once_with(mock_session, fake_embedding, k=settings.top_k)
    assert result == sentinel_result