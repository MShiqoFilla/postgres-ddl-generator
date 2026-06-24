# PostgreSQL DDL Query Generator

## Overview

This tool helps us regenerate DDL query of existing tables in PostgreSQL.

## Preparation

Install uv (if you haven't), you can install it for global environment,
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```
Or create python venv and then install uv via pip.
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install uv
```
And then start install the dependencies
```bash
uv sync
```