import os

os.environ["OPENAI_API_KEY"] = "test_openai_api_key"
os.environ["PORTKEY_API_KEY"] = "test_portkey_api_key"
from kt_generator.open_ai_client import OpenAIClient


class TestOpenAIClient:
    def test_setup_system_initializes_a_non_zero_history(self):
        client = OpenAIClient()
        client.setup_system()
        assert len(client.history) != 0
