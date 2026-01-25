# Interview Preparation Guide: Olist Data Analyst Agent

This guide is designed to help you confidently present your work during an interview. It covers the project's architecture, key technical decisions, and potential questions you might face.

## 🚀 Project Overview

The **Olist Data Analyst** is an AI-powered conversational agent that allows users to query and visualize the Olist E-commerce database using natural language or voice. It leverages state-of-the-art LLMs (local and cloud) via a structured agentic workflow.

### Key Technologies
*   **Orchestration:** [LangGraph](file:///c:/Users/Younis%20AlAzzeh/Desktop/Starting_Script/src/services/data_analyst_agent.py) (handling complex multi-step reasoning)
*   **UI Framework:** [Chainlit](file:///c:/Users/Younis%20AlAzzeh/Desktop/Starting_Script/chainlit_app.py) (streaming, settings, voice integration)
*   **Speech-to-Text:** Local [OpenAI Whisper](file:///c:/Users/Younis%20AlAzzeh/Desktop/Starting_Script/src/services/voice_service.py)
*   **Data/Vix:** SQLite & Plotly
*   **Model Agnostic:** Supporting Ollama, OpenAI, Anthropic, Google GenAI, and Azure.

---

## 🏗️ Technical Architecture

### 1. LangGraph Workflow
The core logic resides in a stateful graph where nodes represent specific actions:
*   **Analyst Node:** The brain of the agent. It receives the conversation history and decides whether to write a SQL query or provide a summary.
*   **Tools Node:** Executes the specialized tools requested by the Analyst.
*   **Conditional Routing:** Determines if the flow should continue (e.g., execute a tool) or finish and reply to the user.

### 2. Specialized Tools
*   **`execute_sql_tool`:** Handles interaction with `olist.sqlite`. It includes logic for formatting results and limiting rows to prevent LLM context overflow.
*   **`draw_chart_tool`:** Converts analyst-generated data into high-quality Plotly visualizations (Bar, Line, Pie, Scatter).

### 3. Voice Integration
A custom `VoiceService` handles local transcription. 
> [!IMPORTANT]
> **Technical Highlight:** The service uses a Singleton pattern to avoid reloading the ~74M parameter Whisper model on every query, ensuring low latency. It also includes automatic FFmpeg detection for robust cross-platform compatibility.

---

## 💡 Potential Interview Questions & Answers

### Q1: Why use LangGraph instead of a simple OpenAI Agent?
**Answer:** LangGraph provides much greater control over the agent's behavior. Unlike standard agents that can "loop" unpredictably, LangGraph uses a structured state machine. This allowed me to enforce a specific workflow: **Analyze -> Execute SQL -> (Optionally) Visualize -> Summarize**. It also makes the application more robust and easier to debug.

### Q2: How do you handle cases where the LLM writes bad SQL?
**Answer:** I implemented several safety layers:
1.  **Strict System Prompting:** The prompt includes explicit SQLite-specific rules (e.g., using `strftime` for dates).
2.  **Error Handling:** If the `execute_sql_tool` fails, the error is returned to the analyst node, allowing the agent to "self-correct" and try a different query approach.
3.  **Schema Context:** I provide a detailed, pre-loaded schema (`schema_output.md`) in the system prompt so the model knows exactly which tables and columns exist.

### Q3: How do you manage large datasets in the LLM context?
**Answer:** I don't send the whole dataset to the model. The `execute_sql_tool` is designed to return only the first 30 rows of a query. If the analyst needs aggregate data (like "total sales per month"), I instruct it to perform the aggregation *inside* the SQL query, so only the summary enters the LLM context.

### Q4: Why did you choose local Whisper for voice transcription?
**Answer:** Two main reasons: **Privacy and Cost**. By running Whisper locally, we don't send audio data over the wire (user privacy) and avoid API token costs. Using the `base` model provides a great balance between speed (near real-time) and accuracy.

---

## 📊 Data Insights (The Market Context)
Be ready to talk about the data you worked with!
*   **Complex Relationships:** Sales are in `order_items`, but delivery status is in `orders`.
*   **Translation Handling:** The dataset has a `product_category_name_translation` table to convert Portuguese categories to English—crucial for international reporting.
*   **Scale:** The database has ~100k customers and nearly as many orders, making it a realistic "Big Data" mock-up.
