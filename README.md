# HelenaBot

**An AI-powered conversational assistant using Retrieval-Augmented Generation (RAG) and Telegram integration, focused on surgical instrumentation and orthopedics.**

HelenaBot is designed to answer natural-language questions using information retrieved from technical and academic PDF documents. It combines document processing, embeddings, semantic search, and large language models (LLMs) in a Telegram-based conversational interface.

> **Status:** Work in progress. The architecture and commands below reflect the repository structure; a complete deployment depends on client-specific configuration and has not been independently validated here.

## Features

- **Conversational Q&A:** Natural-language interaction through Telegram.
- **Text and voice input:** Dedicated handlers for text and voice messages.
- **Retrieval-Augmented Generation (RAG):** Retrieves relevant document passages to ground generated responses.
- **PDF processing:** Extracts and prepares document content, with supporting image-processing utilities.
- **Vector search:** Integrates ChromaDB and Hugging Face embeddings through LlamaIndex.
- **LLM-powered answers:** Uses models accessed through Groq.
- **Client-specific configuration:** Loads settings from the `clients/` directory.
- **Observability:** Includes components for metrics, interaction records, and logging.
- **Webhooks:** Uses Flask and Cloudflare Tunnel integration to receive Telegram updates.

## How It Works

```text
Telegram user
     |
     v
Text / voice message handlers
     |
     v
Question and context preparation
     |
     v
Semantic search over indexed documents
     |
     v
Retrieved passages + prompt
     |
     v
Language model (via Groq)
     |
     v
Response delivered through Telegram
```

The indexing pipeline prepares source documents and their embeddings. During a conversation, the retrieval component searches the indexed content and provides relevant context to the language model. Response accuracy depends on document quality and system configuration; RAG does not eliminate hallucinations or factual errors.

## Tech Stack

| Layer | Technologies |
| --- | --- |
| Language | Python 3.12.7 |
| Chat interface | python-telegram-bot |
| API / webhooks | Flask |
| RAG orchestration | LlamaIndex |
| Embeddings | Hugging Face |
| Vector database | ChromaDB |
| LLM inference | Groq |
| Database | MongoDB / PyMongo |
| PDF and image processing | PyMuPDF, pypdf, pdfminer.six, OpenCV |
| Infrastructure | Docker Compose, Cloudflare Tunnel |
| Testing and code quality | pytest, pytest-cov, pylint |
| Dependency management | Poetry |

## Repository Structure

```text
.
├── clients/                 # Client-specific configurations
├── data/                    # Local documents and generated artifacts
├── scripts/                 # Utility scripts
├── src/helena_bot/
│   ├── bot/                 # Message handlers, responses, and retrieval
│   ├── core/                # Startup, Flask, and webhooks
│   ├── pipeline/            # Document processing and embeddings
│   ├── utils/               # Vector storage, database, metrics, and file utilities
│   ├── document_reader.py
│   └── embedding_config.py
├── tests/                   # Automated tests
├── Dockerfile
├── docker-compose.yml       # MongoDB service
├── Makefile
├── pyproject.toml
└── poetry.lock
```

## Getting Started

### Prerequisites

- Python **3.12.7**, as specified by the project configuration.
- Poetry.
- Docker and Docker Compose if running MongoDB in a container.
- Valid credentials for the external services you intend to use.

Clone the repository over SSH:

```bash
git clone git@github.com:jsantoos/helenabot.git
cd helenabot
```

Install dependencies:

```bash
poetry install
```

Start the MongoDB service defined in the root Compose file:

```bash
docker compose up -d mongodb
```

### Configuration

Set the environment variables required by your selected client and deployment. Examples of variables referenced by the code include:

```dotenv
CLIENT_NAME=your_client_name
TELEGRAM_TOKEN=your_telegram_bot_token
GROQ_API_KEY=your_groq_api_key
MONGO_URL=mongodb://localhost:27017
```

This is an **illustrative example**, not a verified, complete configuration for every client. Review the settings under `clients/`, document paths, and other required variables before running the application. Never commit real credentials.

### Running the Application

The application startup entry point is `helena_bot.core.startup`. After configuring the client and integrations, run:

```bash
poetry run python -m helena_bot.core.startup
```

Startup includes Flask, client configuration, and Telegram webhook registration, which requires a publicly reachable URL. Review your Cloudflare Tunnel configuration before deploying remotely.

> **Note:** The `Makefile` references specific Compose files, such as `docker-compose.mongo.yml` and `clients/.../docker-compose.yml`. Confirm that those files exist and update paths as needed before running `make all`.

## Testing

Run the automated test suite:

```bash
poetry run pytest -q
```

Generate a coverage report (with development dependencies installed):

```bash
poetry run pytest --cov=helena_bot --cov-report=term-missing
```

The presence of automated tests does not imply that the entire suite has been verified to pass in the current environment.

## Example Use Case

**User question:** “What is the purpose of a particular surgical instrument?”

**Expected behavior:** HelenaBot searches its indexed reference material and generates an explanation informed by the retrieved context, when relevant material is available.

The Telegram interface also provides `/ajuda` (help) and `/sobre` (about) commands and supports text or voice messages through the implemented handlers.


## Security and Limitations

- HelenaBot is intended for **educational and reference support**; it is not a substitute for professional medical judgment, advice, or clinical decisions.
- LLM-generated answers may be inaccurate. Verify technical information against authoritative sources.
- Do not index personal or clinical data without appropriate authorization and safeguards.
- Keep API keys, tokens, internal URLs, and private information out of Git history.
- Review copyright and redistribution permissions before committing PDF collections to a public repository.

## Authors and Contributors

Developed by **João Santos**

## License

No distribution license was identified during this review. Add a `LICENSE` file if you intend to specify terms for using, modifying, or redistributing this project.
