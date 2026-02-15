# Run Nexora Search API from project root
Set-Location $PSScriptRoot
python -m uvicorn src.api.routes:app --reload --host 0.0.0.0 --port 8000
