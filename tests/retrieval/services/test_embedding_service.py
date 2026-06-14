from unittest.mock import AsyncMock, patch
from src.retrieval.services.embedding_service import embed_query, embed_document

@patch("src.infrastructure.llm.embed", new_callable=AsyncMock)
async def test_embed_query(mock_embed):
    fake_embedding = [0.1, 0.2, 0.3]
    mock_embed.return_value = fake_embedding
    text = "test query"
    result = await embed_query(text)
    mock_embed.assert_awaited_once_with(text, is_query=True)
    assert result == fake_embedding

@patch("src.infrastructure.llm.embed", new_callable=AsyncMock)
async def test_embed_document(mock_embed):
    fake_embedding = [0.1, 0.2, 0.3]
    mock_embed.return_value = fake_embedding
    text = "test document"
    result = await embed_document(text)
    mock_embed.assert_awaited_once_with(text, is_query=False)
    assert result == fake_embedding