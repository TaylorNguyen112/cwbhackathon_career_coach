from autogen_ext.models.openai import AzureOpenAIChatCompletionClient
from autogen_core.models import ChatCompletionClient
import os

def llm_config(role: str):
    deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT") if role == "agent" else os.getenv("AZURE_OPENAI_TOOL_DEPLOYMENT")
    az_model_client = AzureOpenAIChatCompletionClient(
        azure_deployment=deployment,
        model=deployment,
        api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    )
    return az_model_client


