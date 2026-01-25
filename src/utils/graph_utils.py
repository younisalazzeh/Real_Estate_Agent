"""
LangGraph utility functions for agent workflows.
"""
import os
from typing import Optional, Sequence
from langchain.chat_models import init_chat_model
from langchain_core.messages import BaseMessage, SystemMessage, AIMessage
from langchain_core.runnables import RunnableConfig
from langgraph.graph import MessagesState
from src.logger import setup_application_logger

logger = setup_application_logger(__name__)


# ================================================================================
# Model Configuration
# ================================================================================

def get_model_config(model: str, **kwargs) -> dict:
    """
    Get model configuration based on provider prefix.
    
    Args:
        model: Model string in format "provider:model_name"
        **kwargs: Additional configuration options
        
    Returns:
        Dictionary with model configuration
    """
    provider = model.split(":")[0] if ":" in model else model
    config = {"model": model}
    
    if provider == "anthropic":
        config["api_key"] = os.environ.get("ANTHROPIC_API_KEY")
    elif provider == "google_genai":
        config["api_key"] = os.environ.get("GOOGLE_API_KEY")
    elif provider == "openai":
        config["api_key"] = os.environ.get("OPENAI_API_KEY")
    elif provider == "azure_openai":
        config["api_key"] = os.environ.get("AZURE_OPENAI_API_KEY")
        config["azure_endpoint"] = kwargs.get("azure_endpoint") or os.environ.get("AZURE_OPENAI_ENDPOINT")
        config["api_version"] = kwargs.get("api_version") or os.environ.get("AZURE_OPENAI_API_VERSION", "2024-12-01-preview")
    elif provider == "ollama":
        config["base_url"] = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
    
    # Add any additional kwargs
    for key, value in kwargs.items():
        if key not in config and value is not None:
            config[key] = value
    
    return config


# ================================================================================
# Model Invocation
# ================================================================================

async def call_model(
    state: MessagesState,
    config: RunnableConfig,
    system_message: Optional[str] = None,
    tools: Optional[Sequence] = None
) -> AIMessage:
    """
    Call the LLM with the current state messages and optional tools.
    
    Args:
        state: Current conversation state with messages
        config: Runnable configuration containing model settings
        system_message: Optional system prompt to prepend
        tools: Optional list of tools to bind to the model
        
    Returns:
        AIMessage response from the model
    """
    try:
        # Get model name from config
        configurable = config.get("configurable", {})
        model_name = configurable.get("model_name", "ollama:llama3.1:8b")
        
        logger.info(f"Calling model: {model_name}")
        
        # Initialize the model
        model_config = get_model_config(model_name)
        chat_model = init_chat_model(**model_config)
        
        # Bind tools if provided
        if tools:
            logger.info(f"Binding {len(tools)} tools to model")
            chat_model = chat_model.bind_tools(tools)
        
        # Build messages list
        messages = []
        
        if system_message:
            messages.append(SystemMessage(content=system_message))
        
        # Add state messages
        messages.extend(state["messages"])
        
        # Invoke model
        response = await chat_model.ainvoke(messages)
        
        logger.info(f"Model response received. Has tool calls: {bool(response.tool_calls)}")
        return response
        
    except Exception as e:
        logger.error(f"Error calling model: {str(e)}")
        raise


# ================================================================================
# Conditional Edge Functions
# ================================================================================

def should_continue_tools(state: MessagesState) -> str:
    """
    Determine if the agent should continue to tool execution or end.
    
    Args:
        state: Current conversation state
        
    Returns:
        "continue" if there are tool calls to execute, "end" otherwise
    """
    messages = state["messages"]
    
    if not messages:
        return "end"
    
    last_message = messages[-1]
    
    # Check if the last message has tool calls
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        logger.info(f"Continuing to execute {len(last_message.tool_calls)} tool calls")
        return "continue"
    
    logger.info("No tool calls, ending workflow")
    return "end"
