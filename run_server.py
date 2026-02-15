"""
Run NEXORA from the project root so 'src' is found no matter where you start.
Use this when you run from a different directory (e.g. C:\\Users\\Admin).

  From anywhere:  python d:\\NEXORA\\run_server.py
  From project:    cd d:\\NEXORA   then   python run_server.py
"""
import os
import sys

# Project root = directory where this script lives (d:\NEXORA)
_project_root = os.path.dirname(os.path.abspath(__file__))
os.chdir(_project_root)
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

# Now run the real app
import uvicorn
from src.config import settings

if __name__ == "__main__":
    uvicorn.run(
        "src.api.routes:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True,
    )
