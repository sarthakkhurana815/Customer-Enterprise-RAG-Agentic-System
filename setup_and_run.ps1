$ErrorActionPreference = "Stop"
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe scripts\generate_dataset.py
Write-Host "Setup complete. Next run: .\.venv\Scripts\python.exe -m src.ingestion.build_index"
