# Olist Data Analyst Agent

An intelligent AI-powered data analyst that converts natural language queries into SQL queries, executes them against an Olist E-commerce database, and creates interactive visualizations using LangGraph and Chainlit.

## 🎯 Project Overview

This project demonstrates a production-ready **Natural Language to SQL (NL2SQL)** agent with integrated data visualization capabilities. The agent uses LangGraph for workflow orchestration, supports multiple LLM providers, and provides a user-friendly Chainlit interface with voice input support.

## ✨ Key Features

- **🤖 Intelligent SQL Generation**: Converts natural language to SQLite queries
- **📊 Interactive Visualizations**: Creates Plotly charts (bar, line, scatter, pie) from query results
- **🎤 Voice Input Support**: Transcribe audio queries using Whisper
- **🔄 Multi-Provider LLM Support**: Works with Ollama, OpenAI, Anthropic, Google, Azure
- **💾 Conversation Memory**: Maintains context across multiple queries
- **🛡️ Error Handling**: Robust error handling with clear user feedback
- **📈 Real-time Streaming**: Streams responses for better UX

## 🏗️ Architecture

### Technology Stack

- **LangGraph**: State machine workflow for agent orchestration
- **LangChain**: LLM integration and tool management
- **Chainlit**: Interactive web UI
- **SQLite**: Database backend (Olist E-commerce dataset)
- **Plotly**: Interactive data visualizations
- **Whisper**: Speech-to-text transcription

### Architecture Diagram

```
User Input (Text/Voice)
    ↓
Chainlit UI
    ↓
Data Analyst Agent (LangGraph Workflow)
    ├── Analyst Node (LLM with Tools)
    │   ├── execute_sql_tool
    │   └── draw_chart_tool
    └── Tool Executor Node
        ↓
SQLite Database → Results → Visualization
```

## 📁 Project Structure

```
Starting_Script/
├── chainlit_app.py          # Main Chainlit application
├── requirements.txt          # Python dependencies
├── data/
│   ├── olist.sqlite         # SQLite database
│   └── schema_output.md     # Database schema documentation
├── src/
│   ├── services/
│   │   ├── data_analyst_agent.py  # LangGraph workflow
│   │   └── voice_service.py       # Whisper transcription
│   ├── utils/
│   │   ├── graph_utils.py         # LangGraph helpers
│   │   └── model_utils.py         # LLM configuration
│   ├── prompts.py                  # System prompts
│   └── logger.py                   # Logging setup
└── logs/                           # Application logs
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- FFmpeg (for voice transcription)
- Ollama (optional, for local models)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/younisalazzeh/Real_Estate_Agent.git
   cd Real_Estate_Agent
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up the database**
   - The `olist.sqlite` database is not included (too large for GitHub)
   - Download from [Kaggle: Brazilian E-Commerce Dataset](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)
   - Place the database file at `data/olist.sqlite`
   - See `data/README.md` for more details

4. **Set up environment variables** (optional, for cloud LLMs)
   ```bash
   # Create .env file
   export GOOGLE_API_KEY="your-key"
   export OPENAI_API_KEY="your-key"
   export ANTHROPIC_API_KEY="your-key"
   ```

5. **Run the application**
   ```bash
   chainlit run chainlit_app.py -w
   ```

5. **Open your browser**
   - Navigate to `http://localhost:8000`

## 💡 Usage Examples

### Example 1: Simple Query
```
User: "How many customers are in the database?"

Agent Response:
- Executes: SELECT COUNT(*) FROM customers
- Returns: 99,441 customers
```

### Example 2: Visualization Request
```
User: "Create a bar chart of monthly revenue for 2018"

Agent Response:
1. Executes SQL query to get monthly revenue
2. Creates interactive Plotly bar chart
3. Provides insights and summary
```

### Example 3: Complex Analysis
```
User: "Show me the top 10 cities by number of orders"

Agent Response:
- Joins orders and customers tables
- Groups by city
- Returns ranked results with insights
```

## 🔧 Configuration

### Model Selection

The app supports multiple LLM providers. Configure via Chainlit settings:

- **Ollama** (Local): `ollama:llama3.1:8b`
- **OpenAI**: `openai:gpt-4o`
- **Anthropic**: `anthropic:claude-3-sonnet`
- **Google**: `google_genai:gemini-pro`
- **Azure OpenAI**: `azure_openai:gpt-4`

### Database Schema

The database contains Olist E-commerce data:
- `orders`: Order information
- `order_items`: Order line items with prices
- `customers`: Customer data
- `products`: Product catalog
- `sellers`: Seller information
- `order_payments`: Payment details
- `order_reviews`: Customer reviews

See `data/schema_output.md` for complete schema documentation.

## 🛠️ Technical Highlights

### LangGraph Workflow

The agent uses a state machine pattern:

1. **Analyst Node**: LLM processes user query and decides which tools to use
2. **Tool Executor Node**: Executes SQL queries or creates charts
3. **Conditional Routing**: Automatically routes based on tool calls

### Key Design Decisions

1. **Unified Agent**: Single agent handles both SQL and visualization (no mode switching)
2. **Tool-Based Architecture**: Clean separation of concerns using LangChain tools
3. **Error Prevention**: System prompt enforces SQLite syntax to prevent common errors
4. **No Hallucination**: Insights only generated from actual query results

### Performance Optimizations

- **Streaming Responses**: Real-time token streaming for better UX
- **Query Result Limiting**: Limits displayed rows to prevent UI overload
- **Singleton Workflow**: Reuses compiled workflow instance
- **Memory Checkpointing**: Efficient conversation state management

## 📊 Database Information

- **Type**: SQLite
- **Size**: ~100K orders, ~100K customers
- **Time Period**: 2016-2018
- **Tables**: 11 tables with relationships

### Important SQLite Syntax Notes

The agent is specifically configured for SQLite:
- Uses `strftime('%Y', column)` instead of `YEAR(column)`
- Uses `strftime('%Y-%m', column)` for year-month
- Uses `||` for string concatenation
- Uses `LIMIT n` instead of `TOP n`

## 🧪 Testing

Test the agent with various queries:

```python
# Simple count query
"How many orders were placed in 2018?"

# Aggregation query
"What is the average order value by state?"

# Visualization request
"Show me monthly sales trends as a line chart"

# Complex join query
"Which product categories have the highest revenue?"
```

## 📝 Logging

Application logs are stored in `logs/` directory with daily rotation:
- Format: `YYYY-MM-DD.log`
- Includes: Timestamps, log levels, module names, messages

## 🔒 Security Considerations

- API keys stored in environment variables (not in code)
- `.env` file excluded from version control
- Database path validation
- SQL injection prevention through parameterized queries (via LangChain tools)

## 🚧 Future Enhancements

- [ ] Support for more chart types (heatmap, box plot, etc.)
- [ ] Export functionality (CSV, PDF reports)
- [ ] Multi-database support
- [ ] Query history and favorites
- [ ] Advanced analytics (forecasting, clustering)
- [ ] User authentication and multi-tenancy

## 📄 License

This project is open source and available for educational purposes.

## 👤 Author

**Younis AlAzzeh**

- GitHub: [@younisalazzeh](https://github.com/younisalazzeh)
- Repository: [Real_Estate_Agent](https://github.com/younisalazzeh/Real_Estate_Agent)

## 🙏 Acknowledgments

- Olist for the public e-commerce dataset
- LangChain team for the excellent framework
- Chainlit for the beautiful UI framework
- Plotly for interactive visualizations

---

**Note**: This project was built as a demonstration of modern AI agent architecture using LangGraph, showcasing production-ready patterns for NL2SQL and data visualization.
