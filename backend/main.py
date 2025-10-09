# Entrypoint for FastAPI app
from routes.api import app

# The app is already defined in routes.api, so we just import it
# This allows running with: uvicorn main:app --reload