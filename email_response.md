# Job Application Screening – Complete Email Response

---

Hello Wedad,

My expected salary is in a range between 600 to 800; this is the salary range for this position in the market. For my English proficiency, it is advanced, and we can see that in my score in the IELTS exam which is 6.5. I'm comfortable with working on-site and with the working hours. I have almost 2 years of experience as an AI engineer from LLM improvement using prompt engineering and building real AI projects. The most frameworks and libraries I used are: FastAPI, LLM integrations, and both LangChain and LangGraph.

---

**• Experience building, training, or deploying AI models in production:**

Yes. I have built and deployed AI-powered applications in production settings. A strong example is the **Olist Data Analyst Agent** — a production-ready Natural Language to SQL (NL2SQL) AI agent I developed using **LangGraph** and **Chainlit**, which I deployed as a fully functional, browser-accessible web application.

Key production highlights:
- Designed a **LangGraph state-machine workflow** with two nodes (Analyst + Tool Executor) and conditional routing — an industry-standard, maintainable architecture for agentic systems.
- The agent dynamically decides whether to run a SQL query (`execute_sql_tool`) or generate an interactive visualization (`draw_chart_tool`) based on the user's intent, all in a single unified agent loop.
- Deployed **OpenAI Whisper locally** as a voice transcription service with a singleton pattern to avoid redundant model loads, handling multiple audio formats (WAV, WebM, MP3, PCM16) via an async pipeline.
- Integrated **LangGraph MemorySaver** for conversation history and thread-based session management, keeping multi-turn context consistent across queries.
- Applied robust production practices: async/await throughout for concurrency, daily-rotating log files, SQL injection prevention through parameterized queries, and environment-based API key management (no hardcoded secrets).
- Supported five LLM providers simultaneously — Ollama (local), OpenAI, Anthropic, Google GenAI, and Azure OpenAI — switchable at runtime via the UI, making the system both flexible and cloud-ready.

---

**• Experience with LLMs, NLP, or Generative AI technologies:**

Yes. I have extensive hands-on experience with a wide range of LLM, NLP, and Generative AI technologies, both in personal projects and professional work:

- **LangChain & LangGraph**: Core frameworks I use for orchestrating agentic workflows — tool binding, conditional routing, state machines, streaming event handling, and memory checkpointing.
- **OpenAI GPT-4o**: Integrated via the OpenAI API for high-quality natural language understanding and SQL generation.
- **Anthropic Claude-3-Sonnet**: Integrated as an alternative LLM backend for reasoning-heavy tasks.
- **Google Gemini (GenAI API)**: Connected for multi-modal and generative tasks.
- **Azure OpenAI**: Used for enterprise-grade deployments with endpoint, API version, and key configuration.
- **Ollama (local LLMs)**: Deployed and ran local models (llama3.1:8b, deepseek-r1, qwen2.5) as cost-effective, privacy-preserving inference endpoints.
- **OpenAI Whisper (local NLP)**: Deployed locally for speech-to-text transcription with automatic language detection, supporting multilingual voice input.
- **Prompt Engineering**: Designed comprehensive 150-line system prompts embedding database schemas, SQLite-specific syntax rules, few-shot examples, output formatting guidelines, and anti-hallucination constraints — ensuring reliable, grounded LLM outputs.
- **Tool Calling / Function Calling**: Built and exposed LangChain-decorated tools that LLMs invoke dynamically, with clean parameter extraction and error handling.
- **Generative AI for Insights**: Used LLMs to generate data analysis insights, chart recommendations, and SQL summaries — all grounded in actual query results, not hallucinated.

---

**• Experience working with APIs, backend integrations, or cloud platforms (AWS, GCP, Azure):**

Yes. My experience spans multiple cloud providers and API integrations:

- **OpenAI API**: Integrated GPT-4o for production-quality LLM inference with proper API key management, streaming support, and usage metadata tracking.
- **Anthropic API**: Integrated Claude-3-Sonnet as an LLM backend with LangChain, handling model configuration and async invocation.
- **Google Cloud / GCP (GenAI API)**: Connected Google Gemini via the Google GenAI API for generative AI capabilities.
- **Azure OpenAI**: Integrated Azure-hosted OpenAI models by configuring endpoint URLs, API versions, and deployment names — enterprise deployment experience.
- **FastAPI**: Built RESTful API backends for AI-powered services, exposing AI capabilities as clean, documented HTTP endpoints.
- **Chainlit**: Deployed the full-stack AI application as a web service, managing session state, real-time streaming, and audio upload endpoints.
- **Environment-based secure configuration**: All API keys and cloud credentials managed through environment variables, never committed to source control.
- **Local inference serving with Ollama**: Configured and ran a local model server on `localhost:11434`, demonstrating the ability to manage self-hosted AI inference infrastructure alongside cloud-based options.

---

I look forward to the opportunity to discuss how my experience can contribute to your team's goals.

Best regards,  
Younis AlAzzeh
