# Setup Guide - Free Multimodal RAG

Complete instructions for setting up and running the Free Multimodal RAG system.

## Prerequisites

- **Python 3.10+** — [Download](https://www.python.org/downloads/)
- **Git** — [Download](https://git-scm.com/)
- **Free API Keys** (2 required):
  - Groq API key
  - Google Gemini API key
- Optional: **Ollama** for local LLM fallback — [Download](https://ollama.ai)

## Step 1: Get Your Free API Keys

### Groq API Key
1. Go to [console.groq.com](https://console.groq.com)
2. Sign up with email or GitHub
3. Navigate to **API Keys**
4. Click **Create New API Key**
5. Copy the key (you'll use it in `.env`)

**Free Tier:** 6,000 tokens/minute, unlimited requests

### Google Gemini API Key
1. Go to [aistudio.google.com](https://aistudio.google.com/app/apikey)
2. Click **Get API Key**
3. Click **Create API Key in new project**
4. Copy the key

**Free Tier:** 1,500 requests/day

## Step 2: Clone the Repository

```bash
git clone https://github.com/yourusername/free-multimodal-rag.git
cd free-multimodal-rag
```

## Step 3: Create Virtual Environment

### On Windows:
```bash
python -m venv venv
venv\Scripts\activate
```

### On macOS/Linux:
```bash
python -m venv venv
source venv/bin/activate
```

## Step 4: Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- **PDF Processing:** pymupdf, pdfplumber
- **Embeddings:** sentence-transformers (all-MiniLM-L6-v2)
- **Vector DB:** chromadb
- **LLM APIs:** groq, google-generativeai
- **UI:** streamlit
- **Utilities:** langchain, pandas, pillow

## Step 5: Configure API Keys

1. Copy the environment template:
```bash
cp .env.example .env
```

2. Edit `.env` with your API keys:
```env
GROQ_API_KEY=your-groq-api-key-here
GOOGLE_API_KEY=your-google-gemini-api-key-here
```

3. (Optional) If using Ollama fallback:
```env
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=mistral
```

## Step 6: Optional - Install Ollama for Local LLM Fallback

If you want graceful degradation when Groq API is unavailable:

1. Download **Ollama** from [ollama.ai](https://ollama.ai)
2. Install and start the Ollama service
3. Pull a model:
```bash
ollama pull mistral
```

4. Ollama will run on `http://localhost:11434` (default)

## Step 7: Run the Application

```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`

## Quick Start Workflow

1. **Upload a PDF:**
   - Go to the "Upload PDF" section
   - Select a PDF file
   - Choose a chunking strategy (recommended: `recursive`)
   - Click "Ingest PDF"

2. **Ask Questions:**
   - Enter your question in the chat
   - Click "Search"
   - View the answer with source attribution

3. **Benchmark Chunking:**
   - Go to the "Chunking Benchmark" tab
   - Click "Run Benchmark"
   - Compare fixed, semantic, and recursive strategies

## Project Structure

```
free-multimodal-rag/
├── src/                      # Core modules
│   ├── config.py            # Configuration & API keys
│   ├── pdf_parser.py        # PDF extraction
│   ├── pipeline.py          # End-to-end ingestion
│   ├── retriever.py         # Query & answer synthesis
│   ├── chunking_benchmark.py # Strategy evaluation
│   ├── processors/          # Modality-specific processors
│   │   ├── text_processor.py
│   │   ├── table_processor.py
│   │   ├── image_processor.py
│   │   └── embeddings.py
│   ├── llm/                 # LLM clients
│   │   ├── groq_client.py
│   │   ├── gemini_client.py
│   │   └── fallback_llm.py
│   └── vector_db/           # Vector database
│       └── chromadb_manager.py
├── app.py                   # Streamlit UI entry point
├── tests/                   # Test suite
│   ├── test_pdf_parser.py
│   └── test_integration.py
├── data/
│   ├── samples/            # Test PDFs go here
│   └── chroma_db/          # Local vector DB storage
├── results/                 # Benchmark results
│   └── chunking_benchmark.csv
├── requirements.txt        # Python dependencies
├── .env.example            # API key template
└── README.md              # Main documentation
```

## Troubleshooting

### API Key Not Found
```
Error: GROQ_API_KEY environment variable not set
```
**Solution:** Make sure you've:
1. Created `.env` file in the project root
2. Added your API keys
3. Restarted the app (Ctrl+C and `streamlit run app.py`)

### ChromaDB Permission Error
```
Error: chromadb.db [permission denied]
```
**Solution:**
- Make sure the `data/` directory is writable
- Or specify a different path in `.env`:
```env
CHROMA_DB_PATH=/path/to/data/chroma_db
```

### Ollama Connection Failed
```
Error: Ollama unavailable at http://localhost:11434
```
**Solution:**
- Start Ollama: `ollama serve` (or start the Ollama app)
- Or disable fallback (system will use Groq only)

### Out of Memory on Image Processing
```
PIL Image processing failed
```
**Solution:**
- Use smaller PDFs for testing
- Or reduce image resolution in the PDF beforehand

## Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_pdf_parser.py -v

# Run with coverage
pytest tests/ --cov=src
```

## Performance Tips

1. **Use Semantic Chunking** for better retrieval precision
2. **Batch Process** tables and images to stay within API rate limits
3. **Cache Embeddings** - queries use cached embeddings, no API cost
4. **Monitor API Usage** - check Groq dashboard for token usage
5. **Use Smaller PDFs** for development (< 100 pages recommended)

## Free API Rate Limits

| Service | Free Tier | Monitoring |
|---------|-----------|-----------|
| Groq | 6,000 tokens/min | [console.groq.com](https://console.groq.com) |
| Gemini | 1,500 req/day | [aistudio.google.com](https://aistudio.google.com) |

## Next Steps

- Upload your first PDF
- Ask questions and see the RAG pipeline in action
- Run the chunking benchmark to see which strategy works best for your data
- Customize prompts in `src/llm/` to fit your use case

## Support & Resources

- **GitHub Issues:** [Report bugs](https://github.com/yourusername/free-multimodal-rag/issues)
- **Groq Docs:** [console.groq.com/docs](https://console.groq.com/docs)
- **Gemini Docs:** [ai.google.dev](https://ai.google.dev)
- **ChromaDB Docs:** [docs.trychroma.com](https://docs.trychroma.com)

## FAQ

**Q: Can I use this offline?**
A: Text embeddings run offline. Tables and images require API calls to Groq and Gemini. Text generation can use local Ollama.

**Q: Is there a batch processing mode?**
A: Yes, Phase 6 adds multi-PDF batch support (optional feature).

**Q: Can I self-host this?**
A: Streamlit Cloud has a free tier, or run locally with `streamlit run app.py`.

**Q: What's the cost for 1000 documents?**
A: ~$0 if using Groq + Gemini free tiers (unless you exceed their daily limits).
