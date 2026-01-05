# Azure Standard Scraping

Working with the [Azure Standard](https://www.azurestandard.com) website.

Requirements:
- [Docker](https://www.docker.com)
- [uv](https://docs.astral.sh/uv/)

Local quick start:
1. `docker compose up -d`
2. `uv run ./postgres.py`
3. `uv run ./main.py`

Review the connection credentials for the created postgres DB in the `.env.local` file.
