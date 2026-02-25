Oriflow Beta
==============

Minimal local development and deployment guide.

Quick summary
-------------
- Small workflow engine prototype with:
  - centralized error taxonomy: `Logger/errors/Errors.py`
  - logging pipeline: JSONL + TXT writers in `Logger/LOGGER`
  - plugin discovery in `Nodes/pluginSeeker.py`
  - async Node runtime in `Nodes/node.py`
  - LLM prompt suite in `OriflowPrompts/`
  - minimal FastAPI entrypoint in `main.py` (GET `/health`)

Run locally (dev)
-----------------
Prereqs: Python 3.11, recommended in a venv.

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Start the app (development):

```bash
python3 main.py
# then visit http://127.0.0.1:8000/health
```

Run with Docker
---------------
Build and run image:

```bash
docker build -t oriflow:dev .
docker run --rm -p 8000:8000 oriflow:dev
```

Or use docker-compose (dev, mounts project directory):

```bash
docker-compose up --build
```

Files of interest
-----------------
- `OriflowPrompts/` — LLM prompts (SetupLLM, FixLLM, AdviceLLM, UpdateLLM, SchemaRulePrompts, PluginLists)
- `Schema/` — JSON schema for nodes/workflows and related base classes
- `Logger/` — error definitions and logging implementations
- `Nodes/` — node runtime and plugin seeker
- `Logs/` — `logs.jsonl` and `logs.txt` created by writer tests

Next recommended steps
----------------------
- Add unit tests for writers and error serialization.
- Implement basic plugin stubs (Start, End, HttpRequest, DelayTimer, Transformer).
- Add CI that runs linters/tests and builds Docker image.

If you want, I can now:
- run a local docker build and report output, or
- create a simple plugin stub set, or
- add unit tests and a `pytest` scaffold.
