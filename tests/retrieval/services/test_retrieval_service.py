from unittest.mock import AsyncMock, MagicMock, patch

from src.config import settings
from src.infrastructure.db.repository import Repository
from src.retrieval.services.retrieval_service import get_relevant_chunks


async def test_get_relevant_chunks_wires_embedding_and_repository_correctly():
    fake_embedding = [0.1, 0.2, 0.3]
    fake_chunks = ["sentinel_chunk_1", "sentinel_chunk_2"]

    fake_session = MagicMock()
    fake_context_manager = MagicMock()
    fake_context_manager.__aenter__ = AsyncMock(return_value=fake_session)
    fake_context_manager.__aexit__ = AsyncMock(return_value=None)
    mock_session_factory = MagicMock(return_value=fake_context_manager)

    with (
        patch(
            "src.retrieval.services.embedding_service.embed_query",
            new_callable=AsyncMock,
            return_value=fake_embedding,
        ) as mock_embed_query,
        patch.object(
            Repository, "top_k_chunks", new_callable=AsyncMock, return_value=fake_chunks
        ) as mock_top_k_chunks,
        patch(
            "src.retrieval.services.retrieval_service.async_session_factory",
            mock_session_factory,
        ),
    ):
        result = await get_relevant_chunks("what electives should I take?")

        mock_embed_query.assert_awaited_once_with("what electives should I take?")
        mock_top_k_chunks.assert_awaited_once_with(fake_session, fake_embedding, k=settings.top_k)
        assert result == fake_chunks
