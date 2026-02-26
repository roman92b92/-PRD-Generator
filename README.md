# PRD Generator

A portfolio project — AI-powered Product Requirements Document generator built on the **Anthropic Claude API**.

Describe your product idea, pick a template, and get a complete, production-quality PRD streamed to your browser in real time.



https://github.com/user-attachments/assets/bc0e1561-59dd-40e2-823a-2ff136306aa2



---

## Features

- **4 PRD formats** — Standard (11-section), One-Page, Agile Epic, Feature Brief
- **Real-time streaming** — PRD text streams word by word via Server-Sent Events
- **Claude-powered** — uses claude-sonnet-4-6 (configurable, supports Opus and Haiku too)
- **Export** — Copy to clipboard or download as `.md` file
- **Rendered preview** — markdown is rendered live with marked.js
- **Dark UI** — clean, minimal SaaS-style interface

---

## Quick Start

### 1. Get an Anthropic API key

1. Go to [console.anthropic.com](https://console.anthropic.com)
2. Sign in or create an account
3. Navigate to **API Keys** → **Create Key**
4. Copy your key

### 2. Set up the project

```bash
git clone https://github.com/roman92b92/prd-generator
cd prd-generator

# Install dependencies
pip install -r requirements.txt

# Add your API key
cp config.example.json config.json
# Edit config.json and replace "your-anthropic-api-key-here" with your actual key
```

### 3. Run

```bash
python app.py
```

Open [http://localhost:5000](http://localhost:5000) in your browser.

---

## Configuration

`config.json` :

```json
{
  "api_key": "sk-ant-...",
  "model": "claude-sonnet-4-6"
}
```

You can also set the API key via environment variable:

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
python app.py
```

Available models:

| Model | Speed | Quality |
|-------|-------|---------|
| `claude-sonnet-4-6` | Fast | Excellent (recommended) |
| `claude-opus-4-6` | Slower | Best |
| `claude-haiku-4-5-20251001` | Fastest | Good for drafts |

---

## PRD Templates

| Template | Best For | Sections |
|----------|----------|---------|
| **Standard PRD** | Complex features, 6+ weeks | 11 sections including exec summary, tech specs, GTM |
| **One-Page PRD** | Small features, quick alignment | Problem, solution, scope, risks, timeline |
| **Agile Epic** | Sprint-based delivery | User story map, sprint breakdown, DoD |
| **Feature Brief** | Early exploration, hypothesis | Context, hypothesis, assumptions, next steps |

---

## CLI Usage

You can also generate PRDs directly from the command line:

```bash
python prd_generator.py
```

This runs a built-in sample (Smart Notification Center) and streams the PRD to your terminal.

---

## Architecture

```
prd-generator/
├── prd_generator.py   # Core: Claude API integration, templates, PRDGenerator class
├── app.py             # Flask server, SSE streaming endpoint
├── templates/
│   └── index.html     # Full web UI (streaming, markdown rendering, export)
├── config.example.json
├── requirements.txt
└── README.md
```

**How streaming works:**

1. Browser POSTs form data to `/generate`
2. Flask calls `PRDGenerator.generate_stream()` which opens a Claude streaming session
3. Text chunks are wrapped in SSE format (`data: {"text": "..."}`) and flushed immediately
4. Browser reads the `ReadableStream`, parses SSE events, and appends chunks to the preview
5. On `[DONE]`, the accumulated markdown is rendered with `marked.js`

---

## Tech Stack

- **Backend**: Python, Flask, Anthropic SDK
- **Frontend**: Vanilla JS, pure CSS, marked.js (CDN)
- **AI**: Claude claude-sonnet-4-6 via the Messages API with streaming

---

## License

MIT
