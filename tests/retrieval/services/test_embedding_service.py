from unittest.mock import AsyncMock, patch

from src.retrieval.services.embedding_service import embed_document, embed_query


# for question
async def test_embed_query_calls_llm_embed_with_is_query_true():
    with patch("src.infrastructure.llm.embed", new_callable=AsyncMock) as mock_embed:
        mock_embed.return_value = [0.1, 0.2, 0.3]

        result = await embed_query("what electives should I take?")

        mock_embed.assert_awaited_once_with("what electives should I take?", is_query=True)
        assert result == [0.1, 0.2, 0.3]


# for document
async def test_embed_document_calls_llm_embed_with_is_query_is_false():
    with patch("src.infrastructure.llm.embed", new_callable=AsyncMock) as mock_embed:
        mock_embed.return_value = [0.4, 0.5, 0.6]

        result = await embed_document("some course description text")

        mock_embed.assert_awaited_once_with("some course description text", is_query=False)
        assert result == [0.4, 0.5, 0.6]
