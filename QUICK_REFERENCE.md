# Quick Reference Card - Interview

## 🎯 30-Second Elevator Pitch

"I built an AI-powered data analyst using LangGraph that converts natural language to SQL, executes queries against an Olist E-commerce database, and creates interactive visualizations. It supports multiple LLM providers, voice input, and uses production-ready patterns."

## 🏗️ Architecture (One Sentence Each)

- **LangGraph**: State machine workflow for agent orchestration
- **LangChain Tools**: Structured function calls for SQL and visualization
- **Chainlit**: Chat UI with streaming and voice input
- **SQLite**: Database with 100K+ orders from Olist dataset
- **Plotly**: Interactive charts (bar, line, scatter, pie)

## 🔑 Key Technical Decisions

1. **Unified Agent**: Single agent decides when to query vs. visualize (no mode switching)
2. **LangGraph over While Loop**: Declarative, maintainable, industry-standard
3. **Tool-Based Architecture**: Clean separation of reasoning and execution
4. **SQLite-Specific Prompts**: Prevents syntax errors with explicit rules
5. **No Hallucination**: Insights only from actual query results

## 💡 Top 3 Challenges & Solutions

1. **Model not calling tools** → Simplified tool interface, better prompts
2. **SQL syntax errors** → Added SQLite-specific rules in system prompt
3. **Chart not displaying** → Changed async to sync, simplified parameters

## 📊 Key Metrics

- **Database**: 99,441 orders, 100K+ customers
- **Tables**: 11 tables with relationships
- **LLM Providers**: 5 supported (Ollama, OpenAI, Anthropic, Google, Azure)
- **Chart Types**: 4 (bar, line, scatter, pie)
- **Response Time**: Real-time streaming

## 🚀 Production Improvements (Top 3)

1. **Database**: Move to PostgreSQL with connection pooling
2. **Caching**: Redis for query result caching
3. **Security**: Query whitelisting, rate limiting, audit logs

## 📝 Demo Flow (2 minutes)

1. **Simple Query**: "How many customers are there?" → Shows SQL + result
2. **Visualization**: "Bar chart of monthly revenue 2018" → Shows SQL + chart + insights
3. **Voice Input**: Use microphone → Transcribes and processes
4. **Model Switch**: Change from Ollama to GPT-4 → Shows flexibility

## 🎓 What You Learned

- LangGraph state machine patterns
- Tool design for LLMs
- Prompt engineering best practices
- Production-ready error handling
- Real-time streaming architecture

## 🔧 Tech Stack (One Word Each)

LangGraph | LangChain | Chainlit | SQLite | Plotly | Whisper

---

**Remember**: 
- Be confident about your design decisions
- Acknowledge limitations honestly
- Show enthusiasm for improvements
- Connect technical choices to business value
