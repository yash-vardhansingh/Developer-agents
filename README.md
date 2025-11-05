# Developer-agent

Very small demo: runs a CodeDeveloper agent with a Docker-based CodeExecutor.

Purpose
- Use a model agent to write code, execute it via Docker, and return results.

Quick run
- Requirements: Python 3.10+, Docker, and the autogen-related packages (httpx, autogen-core, autogen-ext, autogen-agentchat).
- Run:

```powershell
python dev.py
```

Notes
- Provide your model base URL and API key via environment variables; avoid hard-coded secrets.
- Docker must be available for the code executor to run tasks.

This repo contains two main entry points:

- `app.py` — Streamlit-based UI that starts a debate and streams messages into a chat-like interface.
- `dev.py` — Agent configuration and a CLI-style runner. Defines a host (Jane) and two debaters (John - pro, Alice - con) using the Autogen agent/chat stack.

Quick notes
- This project expects Python 3.10+.
- You must provide your own model endpoint and API key. Set these as environment variables:
    - DEBATE_BASE_URL — the base URL of your LLM service
    - DEBATE_API_KEY — your API key
    Example (read at runtime):
    ```python
    import os
    base_url = os.environ["DEBATE_BASE_URL"]
    api_key = os.environ["DEBATE_API_KEY"]
    ```
- For local development you can load values from a .env file (do not commit .env) using python-dotenv:
    ```python
    from dotenv import load_dotenv
    load_dotenv()
    ```
- Keep TLS verification enabled — do not use httpx.AsyncClient(verify=False). Store secrets in a secure vault or CI secrets rather than in source control.
- Pin and confirm dependencies in a requirements.txt or your environment manager.
- When developing or testing, prefer mocked or stubbed model clients to avoid accidental use of real keys.
- This project expects Python 3.10+.
- The code in `dev.py` uses custom Autogen-related packages (`autogen_ext`, `autogen_core`, `autogen_agentchat`) and an HTTP client (`httpx`).
- `dev.py` currently contains an API key and a base_url for a private LLM endpoint. Replace these with environment variables before running.

Suggested (example) dependencies
-------------------------------
The exact package names for your Autogen stack may vary. If you have a package manager or environment, prefer installing pinned dependencies. Example:

```powershell
# create and activate venv (Windows PowerShell)
python -m venv .venv; .\.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install streamlit httpx
# Install your autogen packages (replace with correct package names available to you)
pip install autogen-core autogen-ext autogen-agentchat
```

Running
-------

- To run the CLI-style runner (prints streamed chunks to stdout):

```powershell
python dev.py
```

- To run the Streamlit UI in a browser (recommended for interactive viewing):

```powershell
streamlit run app.py
```

Security & configuration
------------------------
- `dev.py` currently inflates a model client with a hard-coded `api_key` and `base_url`. Do not commit real keys to source control. Instead, set them from environment variables or a secure vault. For example:

```python
import os
api_key = os.environ.get("DEBATE_API_KEY")
base_url = os.environ.get("DEBATE_BASE_URL")
```

- The project also sets `httpx.AsyncClient(verify=False)` which disables HTTPS verification — avoid this in production.

Files
-----

- `app.py` — Streamlit UI that drives the debate. Uses `team_config` and `debate` from `dev.py`.
- `dev.py` — Agent setup, streaming helpers, and a small `main()` for testing.

Next steps / suggestions
-----------------------
- Add a `requirements.txt` with exact dependency versions.
- Move secrets to environment variables.
- Add a short test or script to simulate a debate without calling a remote model (for local dev).