import asyncio
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from app.generators.mock_generator import MockLLMGenerator

@pytest.mark.asyncio
async def test_mock_stream_generation():
    generator = MockLLMGenerator()
    tokens = []
    async for token in generator.stream_generate("卡托普利引起干咳", {"entities": ["卡托普利", "干咳"]}):
        tokens.append(token)
    full_text = "".join(tokens)
    assert len(tokens) > 5
    assert "缓激肽" in full_text
    assert "ARB" in full_text

if __name__ == "__main__":
    asyncio.run(test_mock_stream_generation())
    print("[OK] SSE Stream Generator Tests Passed!")
