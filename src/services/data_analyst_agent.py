"""
Data Analyst Agent using LangGraph.
Handles SQL queries and visualizations for the Olist E-commerce database.
"""
import sqlite3
import json
from pathlib import Path
from typing import Annotated, Literal
import plotly.io as pio
import plotly.graph_objects as go
import chainlit as cl
from langchain_core.tools import tool
from langchain_core.messages import AIMessage, ToolMessage, HumanMessage
from langchain_core.runnables import RunnableConfig
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.checkpoint.memory import MemorySaver

from src.prompts import DATA_ANALYST_SYSTEM_PROMPT
from src.utils.graph_utils import call_model
from src.logger import setup_application_logger

logger = setup_application_logger(__name__)

# Database path
DB_PATH = Path(__file__).parent.parent.parent / "data" / "olist.sqlite"


# ================================================================================
# Tools
# ================================================================================

@tool
def execute_sql_tool(
    query: Annotated[str, "The SQLite query to execute against the olist.sqlite database"]
) -> str:
    """
    Execute a SQL query against the Olist SQLite database and return formatted results.
    
    Use this tool to query customer data, orders, products, sellers, payments, reviews.
    Always use SQLite syntax (strftime for dates, not YEAR/MONTH functions).
    
    Returns formatted results with column names and row data.
    """
    try:
        logger.info(f"Executing SQL: {query[:100]}...")
        
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        
        cursor.execute(query)
        results = cursor.fetchall()
        
        if not results:
            conn.close()
            logger.info("Query returned no results")
            return "Query executed successfully. No rows returned."
        
        # Get column names
        column_names = [description[0] for description in cursor.description]
        
        # Format results as a structured string
        result_str = f"Columns: {', '.join(column_names)}\n\n"
        result_str += f"Results ({len(results)} rows):\n"
        
        # Limit to first 30 rows for display
        for row in results[:30]:
            result_str += f"{row}\n"
        
        if len(results) > 30:
            result_str += f"\n... and {len(results) - 30} more rows"
        
        conn.close()
        
        logger.info(f"Query returned {len(results)} rows")
        return result_str
        
    except sqlite3.Error as e:
        error_msg = f"SQL Error: {str(e)}"
        logger.error(error_msg)
        return error_msg
    except Exception as e:
        error_msg = f"Execution Error: {str(e)}"
        logger.error(error_msg)
        return error_msg


@tool
def draw_chart_tool(
    chart_type: Annotated[str, "Type of chart: bar, line, scatter, pie"],
    x_data: Annotated[str, "JSON array of x-axis values, e.g., '[\"Jan\", \"Feb\", \"Mar\"]'"],
    y_data: Annotated[str, "JSON array of y-axis values, e.g., '[100, 200, 300]'"],
    title: Annotated[str, "Chart title"],
    x_label: Annotated[str, "X-axis label"] = "X",
    y_label: Annotated[str, "Y-axis label"] = "Y"
) -> str:
    """
    Create and display a Plotly chart. Call this AFTER getting data from execute_sql_tool.
    
    Args:
        chart_type: bar, line, scatter, or pie
        x_data: JSON array string of x values (categories or labels)
        y_data: JSON array string of y values (numeric data)
        title: Chart title
        x_label: Label for x-axis
        y_label: Label for y-axis
    
    Example: draw_chart_tool("bar", '["Jan", "Feb"]', '[1000, 2000]', "Monthly Revenue", "Month", "Revenue")
    """
    try:
        logger.info(f"Creating {chart_type} chart: {title}")
        
        # Parse JSON arrays
        x_values = json.loads(x_data)
        y_values = json.loads(y_data)
        
        # Create the appropriate chart
        if chart_type.lower() == "bar":
            fig = go.Figure(data=[go.Bar(x=x_values, y=y_values, marker_color='#2E86AB')])
        elif chart_type.lower() == "line":
            fig = go.Figure(data=[go.Scatter(x=x_values, y=y_values, mode='lines+markers', line=dict(color='#2E86AB', width=2))])
        elif chart_type.lower() == "scatter":
            fig = go.Figure(data=[go.Scatter(x=x_values, y=y_values, mode='markers', marker=dict(color='#2E86AB', size=10))])
        elif chart_type.lower() == "pie":
            fig = go.Figure(data=[go.Pie(labels=x_values, values=y_values)])
        else:
            fig = go.Figure(data=[go.Bar(x=x_values, y=y_values, marker_color='#2E86AB')])
        
        # Update layout
        fig.update_layout(
            title=dict(text=title, font=dict(size=18)),
            xaxis_title=x_label,
            yaxis_title=y_label,
            template="plotly_white",
            margin=dict(l=60, r=40, t=80, b=60)
        )
        
        # Store figure in session for later display
        # We can't display directly here because this is a sync function
        # We'll return a marker and handle display in the streaming
        fig_json = pio.to_json(fig)
        
        logger.info("Chart created successfully")
        return f"CHART_CREATED::{fig_json}"
        
    except json.JSONDecodeError as e:
        error_msg = f"Invalid JSON data: {str(e)}. Make sure x_data and y_data are valid JSON arrays."
        logger.error(error_msg)
        return error_msg
    except Exception as e:
        error_msg = f"Chart error: {str(e)}"
        logger.error(error_msg)
        return error_msg


# List of all tools
ALL_TOOLS = [execute_sql_tool, draw_chart_tool]


# ================================================================================
# Agent Nodes
# ================================================================================

async def analyst_node(state: MessagesState, config: RunnableConfig):
    """Main analyst node - calls the LLM with tools."""
    logger.info("Analyst node processing...")
    
    response = await call_model(
        state,
        config,
        system_message=DATA_ANALYST_SYSTEM_PROMPT,
        tools=ALL_TOOLS
    )
    
    return {"messages": [response]}


async def tool_executor_node(state: MessagesState, config: RunnableConfig):
    """Execute tools and return results."""
    logger.info("Tool executor node processing...")
    
    messages = state["messages"]
    last_message = messages[-1]
    
    tool_results = []
    
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        for tool_call in last_message.tool_calls:
            tool_name = tool_call.get("name", "")
            tool_args = tool_call.get("args", {})
            tool_id = tool_call.get("id", "")
            
            logger.info(f"Executing tool: {tool_name} with args: {str(tool_args)[:100]}")
            
            try:
                if tool_name == "execute_sql_tool":
                    result = execute_sql_tool.invoke(tool_args)
                elif tool_name == "draw_chart_tool":
                    result = draw_chart_tool.invoke(tool_args)
                else:
                    result = f"Unknown tool: {tool_name}"
                
                tool_results.append(ToolMessage(content=result, tool_call_id=tool_id))
                logger.info(f"Tool {tool_name} completed successfully")
                
            except Exception as e:
                error_result = f"Tool execution error: {str(e)}"
                logger.error(error_result)
                tool_results.append(ToolMessage(content=error_result, tool_call_id=tool_id))
    
    return {"messages": tool_results}


def should_continue(state: MessagesState) -> Literal["tools", "end"]:
    """Decide whether to continue to tools or end."""
    messages = state["messages"]
    
    if not messages:
        return "end"
    
    last_message = messages[-1]
    
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        logger.info(f"Routing to tools: {len(last_message.tool_calls)} tool calls")
        return "tools"
    
    logger.info("No tool calls, ending")
    return "end"


# ================================================================================
# Workflow Creation
# ================================================================================

def create_data_analyst_workflow(checkpointer=None):
    """Create the Data Analyst LangGraph workflow."""
    logger.info("Creating data analyst workflow...")
    
    workflow = StateGraph(MessagesState)
    
    # Add nodes
    workflow.add_node("analyst", analyst_node)
    workflow.add_node("tools", tool_executor_node)
    
    # Add edges
    workflow.add_edge(START, "analyst")
    workflow.add_conditional_edges("analyst", should_continue, {"tools": "tools", "end": END})
    workflow.add_edge("tools", "analyst")
    
    # Compile
    if checkpointer is None:
        checkpointer = MemorySaver()
    
    compiled = workflow.compile(checkpointer=checkpointer)
    
    logger.info("Workflow created successfully")
    return compiled


# ================================================================================
# Agent Runner
# ================================================================================

_workflow = None


def get_workflow():
    """Get or create the workflow singleton."""
    global _workflow
    if _workflow is None:
        _workflow = create_data_analyst_workflow()
    return _workflow


async def run_data_analyst(
    question: str,
    model_name: str = "ollama:llama3.1:8b",
    thread_id: str = "default"
):
    """
    Run the data analyst agent on a user question.
    Yields chunks for streaming and handles chart display.
    """
    logger.info(f"Running data analyst: model={model_name}, thread={thread_id}")
    
    workflow = get_workflow()
    
    config = {
        "configurable": {
            "model_name": model_name,
            "thread_id": thread_id
        }
    }
    
    input_messages = {"messages": [HumanMessage(content=question)]}
    
    try:
        # Track what we've shown
        shown_sql = False
        pending_chart = None
        
        async for event in workflow.astream_events(input_messages, config=config, version="v2"):
            event_type = event.get("event", "")
            
            # Stream LLM tokens
            if event_type == "on_chat_model_stream":
                chunk = event.get("data", {}).get("chunk")
                if chunk and hasattr(chunk, "content") and chunk.content:
                    content = chunk.content
                    if isinstance(content, str):
                        yield content
                    elif isinstance(content, list):
                        for item in content:
                            if isinstance(item, dict) and "text" in item:
                                yield item["text"]
                            elif isinstance(item, str):
                                yield item
            
            # Show when SQL is being executed
            elif event_type == "on_tool_start":
                tool_name = event.get("name", "")
                tool_input = event.get("data", {}).get("input", {})
                
                if tool_name == "execute_sql_tool" and not shown_sql:
                    query = tool_input.get("query", "")
                    if query:
                        yield f"\n\n**🔍 Executing SQL Query:**\n```sql\n{query}\n```\n"
                        shown_sql = True
                
                elif tool_name == "draw_chart_tool":
                    yield "\n\n**📊 Creating visualization...**\n"
            
            # Handle tool results
            elif event_type == "on_tool_end":
                tool_name = event.get("name", "")
                tool_output = event.get("data", {}).get("output", "")
                
                # Check if chart was created
                if tool_name == "draw_chart_tool" and "CHART_CREATED::" in str(tool_output):
                    try:
                        fig_json = str(tool_output).split("CHART_CREATED::")[1]
                        fig = pio.from_json(fig_json)
                        
                        # Display chart in Chainlit
                        elements = [cl.Plotly(name="chart", figure=fig, display="inline", size="large")]
                        await cl.Message(content="**📊 Visualization**", elements=elements).send()
                        
                        yield "\n✅ Chart displayed above.\n"
                    except Exception as e:
                        logger.error(f"Failed to display chart: {e}")
                        yield f"\n⚠️ Chart creation failed: {e}\n"
        
        logger.info("Data analyst completed")
        
    except Exception as e:
        error_msg = f"\n\n❌ Error: {str(e)}"
        logger.error(f"Data analyst error: {e}")
        yield error_msg


# ================================================================================
# Test function
# ================================================================================

async def test_agent(question: str):
    """Test the agent."""
    print(f"\nQuestion: {question}\n" + "-" * 50)
    async for chunk in run_data_analyst(question):
        print(chunk, end="", flush=True)
    print("\n" + "-" * 50)
