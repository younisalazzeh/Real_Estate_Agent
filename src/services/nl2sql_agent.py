import sqlite3
import json
import re
from pathlib import Path
from typing import Annotated, Optional
import plotly.graph_objects as go
import plotly.io as pio
import chainlit as cl
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage, BaseMessage
from src.utils.model_utils import stream_chat_model
from src.logger import setup_application_logger

logger = setup_application_logger(__name__)

DB_PATH = Path(__file__).parent.parent.parent / "data" / "olist.sqlite"
SCHEMA_PATH = Path(__file__).parent.parent.parent / "data" / "schema_output.md"

# ===============================
# SQL Execution Tool
# ===============================

@tool
def execute_sql(
    query: Annotated[str, "The SQL query to execute against the olist.sqlite database"]
) -> str:
    """Execute SQL queries against the olist.sqlite database and return formatted results."""
    try:
        logger.info(f"Executing SQL query: {query}")

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute(query)
        results = cursor.fetchall()

        if not results:
            logger.info("Query executed successfully with no results")
            return "Query executed successfully. No rows returned."

        column_names = [description[0] for description in cursor.description]

        result_str = f"Columns: {', '.join(column_names)}\n\n"
        result_str += f"Rows ({len(results)} total):\n"

        for row in results[:100]:
            result_str += f"{row}\n"

        if len(results) > 100:
            result_str += f"\n... and {len(results) - 100} more rows"

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

# ===============================
# Plotly Chart Generation Tool
# ===============================

@tool
async def generate_plotly_chart(
    query_results: Annotated[str, "The SQL query results to visualize or a SQL query to execute and visualize"],
    chart_type: Annotated[str, "Type of chart: bar, line, scatter, pie, histogram, box, heatmap, area, bubble"],
    x_column: Annotated[Optional[str], "Column name for x-axis"] = None,
    y_column: Annotated[Optional[str], "Column name for y-axis"] = None,
    title: Annotated[Optional[str], "Chart title"] = None,
    x_label: Annotated[Optional[str], "X-axis label"] = None,
    y_label: Annotated[Optional[str], "Y-axis label"] = None
) -> str:
    """Generate a Plotly chart specification as JSON from SQL query results and display it directly in Chainlit."""
    try:
        logger.info(f"Generating {chart_type} chart")
        
        # SELF-HEALING: If query_results looks like a SQL query or a tool call string, execute it first
        import re
        q_cleaned = query_results.strip().upper()
        if "SELECT" in q_cleaned and "FROM" in q_cleaned and not q_cleaned.startswith("COLUMNS:"):
            logger.warning("Detected SQL query instead of results in chart tool. Executing SQL first.")
            # Extract query from execute_sql(query="...") style strings
            sql_match = re.search(r'query=["\'](.*?)["\']', query_results, re.DOTALL | re.IGNORECASE)
            if sql_match:
                query_to_run = sql_match.group(1)
            else:
                # If it's just raw SQL
                query_to_run = query_results
                
            query_results = execute_sql.invoke({"query": query_to_run})
            logger.info("SQL auto-executed successfully for chart.")

        logger.debug(f"Query results preview: {query_results[:200]}")

        lines = query_results.strip().split('\n')
        if len(lines) < 3:
            error_msg = f"Insufficient data for visualization. Got {len(lines)} lines."
            logger.error(error_msg)
            return json.dumps({"error": error_msg})

        column_line = lines[0]
        if not column_line.startswith("Columns:"):
            error_msg = f"Invalid query results format. First line: {column_line}"
            logger.error(error_msg)
            return json.dumps({"error": error_msg})

        columns = [col.strip() for col in column_line.replace("Columns:", "").split(',')]

        data_start_idx = None
        for i, line in enumerate(lines):
            if line.startswith("Rows"):
                data_start_idx = i + 1
                break

        if data_start_idx is None:
            data_start_idx = 2

        data_lines = []
        for line in lines[data_start_idx:]:
            if line.strip() and not line.startswith("..."):
                data_lines.append(line)

        if not data_lines:
            error_msg = "No data rows found"
            logger.error(error_msg)
            return json.dumps({"error": error_msg})

        rows = []
        for line in data_lines:
            line = line.strip()
            if line.startswith('(') and line.endswith(')'):
                line = line[1:-1]

            parts = re.findall(r"'[^']*'|\S+", line)

            values = []
            for part in parts:
                val = part.strip(',').strip().strip("'\"")
                if not val:
                    continue
                try:
                    if '.' in val and val.replace('.', '').replace('-', '').isdigit():
                        values.append(float(val))
                    elif val.replace('-', '').isdigit():
                        values.append(int(val))
                    else:
                        values.append(val)
                except (ValueError, AttributeError):
                    values.append(val)

            if values:
                rows.append(values)

        if not x_column and len(columns) > 0:
            x_column = columns[0]
        if not y_column and len(columns) > 1:
            y_column = columns[1]

        x_idx = columns.index(x_column) if x_column in columns else 0
        y_idx = columns.index(y_column) if y_column in columns else 1

        x_data = [row[x_idx] for row in rows if len(row) > x_idx]
        y_data = [row[y_idx] for row in rows if len(row) > y_idx]

        medical_color_scheme = {
            'primary': '#2E86AB',
            'secondary': '#A23B72',
            'success': '#06A77D',
            'warning': '#F18F01',
            'danger': '#C73E1D',
            'info': '#6A4C93'
        }

        fig = None

        if chart_type.lower() == 'bar':
            fig = go.Figure(data=[go.Bar(
                x=x_data,
                y=y_data,
                marker_color=medical_color_scheme['primary'],
                text=y_data,
                textposition='auto'
            )])

        elif chart_type.lower() == 'line':
            fig = go.Figure(data=[go.Scatter(
                x=x_data,
                y=y_data,
                mode='lines+markers',
                line=dict(color=medical_color_scheme['primary'], width=2),
                marker=dict(size=8)
            )])

        elif chart_type.lower() == 'scatter':
            fig = go.Figure(data=[go.Scatter(
                x=x_data,
                y=y_data,
                mode='markers',
                marker=dict(
                    size=10,
                    color=medical_color_scheme['info'],
                    opacity=0.7
                )
            )])

        elif chart_type.lower() == 'pie':
            fig = go.Figure(data=[go.Pie(
                labels=x_data,
                values=y_data,
                marker=dict(colors=[
                    medical_color_scheme['primary'],
                    medical_color_scheme['secondary'],
                    medical_color_scheme['success'],
                    medical_color_scheme['warning'],
                    medical_color_scheme['danger'],
                    medical_color_scheme['info']
                ]),
                textinfo='label+percent',
                hoverinfo='label+value+percent'
            )])

        elif chart_type.lower() == 'histogram':
            fig = go.Figure(data=[go.Histogram(
                x=x_data,
                marker_color=medical_color_scheme['primary'],
                nbinsx=20
            )])

        elif chart_type.lower() == 'box':
            fig = go.Figure(data=[go.Box(
                y=y_data,
                name=y_column or 'Data',
                marker_color=medical_color_scheme['primary']
            )])

        elif chart_type.lower() == 'area':
            fig = go.Figure(data=[go.Scatter(
                x=x_data,
                y=y_data,
                mode='lines',
                fill='tozeroy',
                line=dict(color=medical_color_scheme['primary']),
                fillcolor=f"rgba(46, 134, 171, 0.3)"
            )])

        elif chart_type.lower() == 'heatmap':
            z_data = [[row[i] for i in range(len(row)) if isinstance(row[i], (int, float))] for row in rows]
            fig = go.Figure(data=[go.Heatmap(
                z=z_data,
                colorscale='Blues'
            )])

        else:
            fig = go.Figure(data=[go.Bar(x=x_data, y=y_data)])

        if not title:
            title = f"{y_column or 'Value'} by {x_column or 'Category'}"

        fig.update_layout(
            title=dict(
                text=title,
                font=dict(size=18, family='Arial, sans-serif', color='#333333')
            ),
            xaxis_title=x_label or x_column or 'X Axis',
            yaxis_title=y_label or y_column or 'Y Axis',
            font=dict(family='Arial, sans-serif', size=12, color='#555555'),
            plot_bgcolor='rgba(240, 240, 240, 0.5)',
            paper_bgcolor='white',
            hovermode='closest',
            showlegend=True if chart_type.lower() in ['line', 'scatter'] else False,
            margin=dict(l=60, r=40, t=80, b=60)
        )

        fig.update_xaxes(
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(200, 200, 200, 0.3)',
            showline=True,
            linewidth=1,
            linecolor='#CCCCCC'
        )

        fig.update_yaxes(
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(200, 200, 200, 0.3)',
            showline=True,
            linewidth=1,
            linecolor='#CCCCCC'
        )

        fig_json = pio.to_json(fig)

        elements = [
            cl.Plotly(
                name=f"{chart_type}_visualization",
                figure=fig,
                display="inline",
                size="large"
            )
        ]

        chart_message = cl.Message(
            content=f"**📊 {chart_type.title()} Chart**",
            elements=elements
        )
        await chart_message.send()

        logger.info(f"Successfully generated and displayed {chart_type} chart in Chainlit")
        return json.dumps({"status": "success", "chart_type": chart_type, "message": "Chart displayed in Chainlit"})

    except Exception as e:
        error_msg = f"Chart generation error: {str(e)}"
        logger.error(error_msg)
        return json.dumps({"error": error_msg})

# ===============================
# NL2SQL Agent
# ===============================

async def nl2sql_agent(
    question: str,
    model: str = "google_genai:gemini-3-flash-preview",
    message_history: Optional[list[BaseMessage]] = None,
    **kwargs
):
    try:
        logger.info(f"Starting NL2SQL agent for question: {question}")

        schema = SCHEMA_PATH.read_text()

        system_prompt = f"""You are a senior SQL Analyst for the Olist E-commerce database.

DATABASE SCHEMA:
{schema}

ANALYSIS RULES:
1. DATA RETRIEVAL: Always use `execute_sql` for ANY technical query. Do NOT explain why you are doing it, just run the query.
2. VISUALIZATION: If the user asks for a chart, trend, plot, or comparison, you MUST call `generate_plotly_chart`. Never say it is "not needed".
3. NO RAW DATA: Never output large JSON blocks in your final response.
4. CHAIN OF THOUGHT: Stream your step-by-step plan before using any tool.

CORRECT TOOL CALL EXAMPLE:
{{"name": "execute_sql", "args": {{"query": "SELECT count(*) FROM orders"}}}}
"""

        from langchain_core.messages import SystemMessage

        if message_history:
            messages = [SystemMessage(content=system_prompt)] + message_history + [HumanMessage(content=question)]
        else:
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=question)
            ]
            
        # --- BALANCED VISUALIZATION TRIGGER ---
        # Only add instructions if keywords are present, but don't show "not needed" in final output
        viz_keywords = ["chart", "plot", "graph", "trend", "visualize", "bar", "line", "pie", "histogram"]
        is_viz_requested = any(word in question.lower() for word in viz_keywords)
        
        if is_viz_requested:
            logger.info("Visualization keyword detected. Adding guidance.")
            messages.append(SystemMessage(content="The user has asked for a visualization. Please prioritize using the 'generate_plotly_chart' tool after you have the data results."))
            
        tools = [execute_sql, generate_plotly_chart]
        max_iterations = 5
        iteration = 0

        while iteration < max_iterations:
            iteration += 1
            logger.info(f"Agent iteration {iteration}")

            full_response = ""
            tool_calls = []

            async for chunk in stream_chat_model(
                messages=messages,
                model=model,
                tools=tools,
                **kwargs
            ):
                if hasattr(chunk, 'content') and chunk.content:
                    content = chunk.content
                    if isinstance(content, list):
                        content = "".join([str(p.get('text', p)) if isinstance(p, dict) else str(p) for p in content])
                    full_response += content
                    # yield content (Suppressed to keep UI clean)

                if hasattr(chunk, 'tool_calls') and chunk.tool_calls:
                    tool_calls.extend(chunk.tool_calls)

            # --- ROBUST TOOL EXTRACTION FOR 1B MODELS ---
            if not tool_calls:
                import json, re, time
                
                # Fallback 1: Extract SQL from code blocks
                sql_match = re.search(r'```sql\s*([\s\S]*?)\s*```', full_response, re.IGNORECASE)
                if sql_match:
                    query = sql_match.group(1).strip()
                    if query and "SELECT" in query.upper():
                        logger.info("Extracted SQL from code block")
                        tool_calls = [{"name": "execute_sql", "args": {"query": query}, "id": f"sql_{int(time.time())}"}]
                
                # Fallback 2: Extract JSON tool calls
                if not tool_calls:
                    matches = re.findall(r'\{[\s\S]*?\}', full_response)
                    for match in matches:
                        try:
                            data = json.loads(match)
                            name = data.get("function") or data.get("name") or ""
                            if "sql" in name.lower() or "execute" in name.lower():
                                params = data.get("parameters") or data.get("args") or data
                                q = params.get("query") if isinstance(params, dict) else ""
                                if q:
                                    tool_calls = [{"name": "execute_sql", "args": {"query": q}, "id": f"jsql_{int(time.time())}"}]
                                    break
                            elif "chart" in name.lower() or "plot" in name.lower():
                                tool_calls = [{"name": "generate_plotly_chart", "args": data.get("args", {}), "id": f"jplot_{int(time.time())}"}]
                                break
                        except: continue

            # --- SILENT ENFORCEMENT ---
            has_viz_call = any(tc.get('name') == 'generate_plotly_chart' for tc in tool_calls)
            is_retrying_viz = False
            
            if is_viz_requested and not has_viz_call and iteration == 1:
                logger.warning("Visualization requested but missed. Retrying silently.")
                messages.append(AIMessage(content=f"Preparing results. {full_response}"))
                messages.append(SystemMessage(content="The user explicitly requested a chart/trend. Please call 'generate_plotly_chart' now using the data you just retrieved."))
                is_retrying_viz = True
            
            if not tool_calls and not is_retrying_viz:
                logger.info(f"Agent iteration {iteration} - No tools called. Response length: {len(full_response)}")
                break


            valid_tool_calls = []
            for tool_call in tool_calls:
                tool_call_id = tool_call.get('id')
                tool_name = tool_call.get('name')

                # Fix common hallucinations for smaller models
                if tool_name:
                    original_name = tool_name
                    # Normalize common variations
                    tool_name = tool_name.lower().replace(" ", "_").replace("-", "_")
                    if "execute" in tool_name and "sql" in tool_name:
                        tool_name = "execute_sql"
                    elif "plotly" in tool_name or "chart" in tool_name:
                        tool_name = "generate_plotly_chart"
                    
                    if tool_name != original_name:
                        logger.info(f"Normalized tool name from '{original_name}' to '{tool_name}'")
                        tool_call['name'] = tool_name

                if not tool_call_id:
                    tool_call['id'] = f"call_{int(time.time())}"
                    tool_call_id = tool_call['id']

                if not tool_name:
                    continue

                valid_tool_calls.append(tool_call)

            if not valid_tool_calls:
                break

            ai_message = AIMessage(content=full_response, tool_calls=valid_tool_calls)
            messages.append(ai_message)

            for tool_call in valid_tool_calls:
                try:
                    tool_call_id = tool_call['id']
                    tool_name = tool_call['name']

                    logger.info(f"Executing tool: {tool_name}")
                    tool_args = tool_call.get('args', {})
                    
                    # Fix parameters being passed as the entire object or nested
                    if isinstance(tool_args, dict) and any(k in tool_args for k in ["function", "parameters", "args"]):
                        logger.warning(f"Suspected nested tool call args for {tool_name}. Flattening.")
                        inner = tool_args.get("parameters") or tool_args.get("args") or tool_args
                        if isinstance(inner, dict):
                            tool_args = inner

                    if tool_name == 'execute_sql':
                        if not tool_args or 'query' not in tool_args:
                            # Try to extract query from string or other fields
                            if isinstance(tool_args, str):
                                tool_args = {"query": tool_args}
                            elif isinstance(tool_args, dict):
                                for v in tool_args.values():
                                    if isinstance(v, str) and "SELECT" in v.upper():
                                        tool_args = {"query": v}; break
                        
                        if not isinstance(tool_args, dict) or 'query' not in tool_args:
                            tool_result = "Error: Missing 'query' parameter"
                        else:
                            tool_result = execute_sql.invoke(tool_args)

                        tool_message = ToolMessage(content=tool_result, tool_call_id=tool_call_id)
                        messages.append(tool_message)

                        yield {
                            "type": "tool_call",
                            "query": tool_args.get('query', 'N/A'),
                            "result": tool_result
                        }

                    elif tool_name == 'generate_plotly_chart':
                        # Fix for list-based params
                        if isinstance(tool_args, list):
                            tool_args = {p["name"]: (p.get("object") or p.get("value")) for p in tool_args if "name" in p}
                            
                        # Missing data recovery
                        if "query_results" not in tool_args:
                            for msg in reversed(messages):
                                if isinstance(msg, ToolMessage) and "Columns:" in str(msg.content):
                                    tool_args["query_results"] = msg.content; break
                        
                        tool_args["chart_type"] = tool_args.get("chart_type", "bar")

                        tool_result = await generate_plotly_chart.ainvoke(tool_args)
                        tool_message = ToolMessage(content=tool_result, tool_call_id=tool_call_id)
                        messages.append(tool_message)

                    else:
                        tool_result = "Unknown tool"
                        tool_message = ToolMessage(content=tool_result, tool_call_id=tool_call_id)
                        messages.append(tool_message)

                except Exception as e:
                    error_msg = f"Tool execution error: {str(e)}"
                    logger.error(error_msg)
                    tool_message = ToolMessage(content=error_msg, tool_call_id=tool_call_id)
                    messages.append(tool_message)
                    yield {"type": "tool_call", "query": "Error", "result": error_msg}

        # --- FINAL RESPONSE CONSTRUCTION ---
        sql_query = ""
        for msg in messages:
            if isinstance(msg, AIMessage) and msg.tool_calls:
                for tc in msg.tool_calls:
                    if tc.get('name') == 'execute_sql':
                        sql_query = tc.get('args', {}).get('query', "")
                        break
        
        formatted_output = "\n\n"
        if sql_query:
            formatted_output += f"1. **🔍 SQL Query**:\n```sql\n{sql_query}\n```\n"
        
        has_chart = any(isinstance(m, ToolMessage) and "plotly" in str(m.content).lower() for m in messages)
        if has_chart:
            formatted_output += "2. **📊 Visualization**: Generated a Plotly chart below.\n"
            
        final_prompt = "Provide 3 key insights as bullet points and a 2-sentence summary of the results. Be brief."
        messages.append(HumanMessage(content=final_prompt))
        
        summary_content = ""
        async for chunk in stream_chat_model(messages=messages, model=model, **kwargs):
            if hasattr(chunk, 'content') and chunk.content:
                summary_content += str(chunk.content)
        
        formatted_output += f"3. **💡 Insights & Summary**:\n{summary_content}"
        yield "\n\n---" + formatted_output

        if len(messages) > 10: messages = [messages[0]] + messages[-9:]
        yield {"type": "memory", "messages": messages}
        logger.info("Agent completed")

    except Exception as e:
        logger.error(f"Agent error: {str(e)}")
        yield f"\n\nError: {str(e)}"


# async def main():
#     question = "What are the top 5 cities by number of customers?"
#     async for chunk in nl2sql_agent(question):
#         print(chunk, end="", flush=True)
