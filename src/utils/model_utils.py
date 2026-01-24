import os
from typing import Optional
from langchain.chat_models import init_chat_model
from langchain_core.callbacks import UsageMetadataCallbackHandler
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from src.logger import setup_application_logger

logger = setup_application_logger(__name__)

# ===============================
# Model Configuration Helper
# ===============================

def get_model_config(model: str, api_key: Optional[str] = None, **kwargs) -> dict:
    try:
        provider = model.split(":")[0] if ":" in model else model
        logger.info(f"Configuring model for provider: {provider}")
        
        config = {"model": model}
        
        if api_key:
            config["api_key"] = api_key
        elif provider == "anthropic":
            config["api_key"] = os.environ.get("ANTHROPIC_API_KEY")
        elif provider == "google_genai":
            config["api_key"] = os.environ.get("GOOGLE_API_KEY")
        elif provider == "openai":
            config["api_key"] = os.environ.get("OPENAI_API_KEY")
        elif provider == "azure_openai":
            config["api_key"] = os.environ.get("AZURE_OPENAI_API_KEY")
            if "azure_endpoint" not in kwargs:
                config["azure_endpoint"] = os.environ.get("AZURE_OPENAI_ENDPOINT")
            if "api_version" not in kwargs:
                config["api_version"] = os.environ.get("AZURE_OPENAI_API_VERSION", "2025-01-01-preview")
        elif provider == "ollama":
            # Ollama runs locally, no API key needed
            config["base_url"] = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
            # Remove api_key from config as Ollama doesn't need it
            config.pop("api_key", None)
        
        for key, value in kwargs.items():
            if key not in config and value is not None:
                config[key] = value
        
        logger.info(f"Model configuration complete for {provider}")
        return config
        
    except Exception as e:
        logger.error(f"Failed to configure model: {str(e)}")
        raise

# config = get_model_config("azure_openai:gpt-4.1")
# config = get_model_config("anthropic:claude-3-5-sonnet-20241022")
# config = get_model_config("google_genai:gemini-3-pro-preview")

# ===============================
# Model Invocation
# ===============================

async def invoke_chat_model(
    messages: list[BaseMessage],
    model: str,
    api_key: Optional[str] = None,
    **kwargs
) -> tuple[AIMessage, dict]:
    try:
        logger.info(f"Initializing chat model: {model}")
        
        model_config = get_model_config(model, api_key, **kwargs)
        
        tools = kwargs.pop('tools', None)
        structured_output = kwargs.pop('structured_output', None)
        
        init_params = {k: v for k, v in model_config.items() if k not in ['tools', 'structured_output']}
        
        chat_model = init_chat_model(**init_params)
        
        if tools:
            logger.info(f"Binding tools to chat model: {tools}")
            chat_model = chat_model.bind_tools(tools)
        
        if structured_output:
            logger.info(f"Configuring structured output: {structured_output}")
            chat_model = chat_model.with_structured_output(structured_output, include_raw=True)

        callback = UsageMetadataCallbackHandler()

        logger.info(f"Invoking chat model with {len(messages)} messages")
        response = await chat_model.ainvoke(messages, config={"callbacks": [callback]})
        
        logger.info("Chat model invocation successful")
        logger.debug(f"Response type: {type(response)}")
        
        return response, callback.usage_metadata
        
    except Exception as e:
        logger.error(f"Failed to invoke chat model '{model}': {str(e)}")
        logger.debug(f"Error details - messages count: {len(messages) if messages else 0}")
        raise

# messages = [HumanMessage(content="What is the capital of France?")]
# response, usage = await invoke_chat_model(messages, "azure_openai:gpt-4.1", api_key=os.environ.get("AZURE_OPENAI_API_KEY"), api_version="2025-01-01-preview", azure_endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT"))

# ===============================
# Model Streaming
# ===============================

async def stream_chat_model(
    messages: list[BaseMessage],
    model: str,
    api_key: Optional[str] = None,
    **kwargs
):
    try:
        logger.info(f"Initializing chat model for streaming: {model}")
        
        model_config = get_model_config(model, api_key, **kwargs)
        
        tools = kwargs.pop('tools', None)
        structured_output = kwargs.pop('structured_output', None)
        
        init_params = {k: v for k, v in model_config.items() if k not in ['tools', 'structured_output']}
        
        chat_model = init_chat_model(**init_params)
        
        if tools:
            logger.info(f"Binding tools to chat model: {tools}")
            chat_model = chat_model.bind_tools(tools)
        
        if structured_output:
            logger.info(f"Configuring structured output: {structured_output}")
            chat_model = chat_model.with_structured_output(structured_output, include_raw=True)

        callback = UsageMetadataCallbackHandler()

        logger.info(f"Starting stream for chat model with {len(messages)} messages")
        
        async for chunk in chat_model.astream(messages, config={"callbacks": [callback]}):
            yield chunk
        
        logger.info("Chat model streaming completed successfully")
        
    except Exception as e:
        logger.error(f"Failed to stream chat model '{model}': {str(e)}")
        logger.debug(f"Error details - messages count: {len(messages) if messages else 0}")
        raise

# messages = [HumanMessage(content="Tell me a story")]
# async for chunk in stream_chat_model(messages, "azure_openai:gpt-4.1", api_key=os.environ.get("AZURE_OPENAI_API_KEY"), api_version="2025-01-01-preview", azure_endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT")):
#     print(chunk.content, end="", flush=True)