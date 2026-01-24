import os
import json
import re
from typing import Optional
from dotenv import load_dotenv
import plotly.io as pio
import chainlit as cl
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, BaseMessage
from src.logger import setup_application_logger
from src.utils.model_utils import stream_chat_model
from src.prompts import PLOTTING_AGENT_SYSTEM_PROMPT

load_dotenv()
logger = setup_application_logger(__name__)

# ===============================
# Plotly JSON Extraction
# ===============================

def extract_plotly_json(response_text: str) -> Optional[str]:
    try:
        logger.info("Extracting Plotly JSON from response")

        json_pattern = r'```(?:json)?\s*(\{.*?\})\s*```'
        match = re.search(json_pattern, response_text, re.DOTALL)

        if match:
            json_str = match.group(1)
            logger.info("Found JSON in code block")
        else:
            json_str = response_text.strip()
            logger.info("Using entire response as JSON")

        json.loads(json_str)
        logger.info("Valid JSON extracted successfully")
        return json_str

    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in response: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Failed to extract JSON: {str(e)}")
        return None

# ===============================
# Plotting Agent Core
# ===============================

async def plotting_agent(
    user_query: str,
    data_context: Optional[str] = None,
    model: str = "google_genai:gemini-3-flash-preview",
    message_history: Optional[list[BaseMessage]] = None,
    **kwargs
):
    try:
        logger.info(f"Starting plotting agent with query: {user_query[:100]}")

        messages = []

        if message_history:
            messages = message_history.copy()

        messages.append(SystemMessage(content=PLOTTING_AGENT_SYSTEM_PROMPT))

        if data_context:
            full_prompt = f"""User Request: {user_query}

Data Context:
{data_context}

Generate a Plotly chart specification in JSON format based on the above request and data."""
        else:
            full_prompt = f"""User Request: {user_query}

Generate a Plotly chart specification in JSON format based on the above request."""

        messages.append(HumanMessage(content=full_prompt))

        full_response = ""

        async for chunk in stream_chat_model(
            messages=messages,
            model=model,
            **kwargs
        ):
            if hasattr(chunk, 'content') and chunk.content:
                content = chunk.content
                if isinstance(content, list):
                    text_parts = []
                    for item in content:
                        if isinstance(item, dict) and 'text' in item:
                            text_parts.append(item['text'])
                        elif isinstance(item, str):
                            text_parts.append(item)
                        else:
                            text_parts.append(str(item))
                    content = "".join(text_parts)

                full_response += content
                yield content

        plotly_json = extract_plotly_json(full_response)

        if plotly_json:
            try:
                fig = pio.from_json(plotly_json)

                elements = [
                    cl.Plotly(
                        name="visualization",
                        figure=fig,
                        display="inline",
                        size="large"
                    )
                ]

                chart_message = cl.Message(
                    content="**📊 Generated Visualization**",
                    elements=elements
                )
                await chart_message.send()

                logger.info("Successfully displayed visualization in Chainlit")
                yield {"type": "visualization", "status": "success", "plotly_json": plotly_json}

            except Exception as e:
                logger.error(f"Failed to display visualization: {str(e)}")
                yield {"type": "visualization", "status": "error", "message": str(e)}
        else:
            logger.warning("No valid Plotly JSON extracted from response")
            yield {"type": "visualization", "status": "error", "message": "Failed to extract valid visualization"}

        messages_to_store = messages + [AIMessage(content=full_response)]
        if len(messages_to_store) > 10:
            messages_to_store = [messages_to_store[0]] + messages_to_store[-9:]

        yield {"type": "memory", "messages": messages_to_store}

        logger.info("Plotting agent execution completed")

    except Exception as e:
        logger.error(f"Plotting agent execution failed: {str(e)}")
        yield f"\n\nVisualization generation failed: {str(e)}"

# ===============================
# Complete Visualization Pipeline
# ===============================

async def generate_visualization(
    user_query: str,
    data_context: Optional[str] = None,
    model: str = "google_genai:gemini-3-flash-preview"
) -> tuple[bool, str, Optional[str]]:
    try:
        logger.info(f"Generating visualization for: {user_query[:100]}")

        full_response = ""
        plotly_json = None

        async for chunk in plotting_agent(
            user_query=user_query,
            data_context=data_context,
            model=model
        ):
            if isinstance(chunk, dict):
                if chunk.get("type") == "visualization":
                    if chunk.get("status") == "success":
                        plotly_json = chunk.get("plotly_json")
                    else:
                        return False, chunk.get("message", "Failed to generate visualization"), None
            elif isinstance(chunk, str):
                full_response += chunk

        if not plotly_json:
            logger.error("No valid Plotly JSON generated")
            return False, "Generated response was not valid Plotly JSON", full_response

        logger.info("Visualization generated successfully")
        return True, "Visualization generated successfully", plotly_json

    except Exception as e:
        logger.error(f"Visualization generation failed: {str(e)}")
        return False, f"Error: {str(e)}", None
