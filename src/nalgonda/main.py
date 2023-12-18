import logging

from fastapi import FastAPI

from nalgonda.constants import DATA_DIR
from nalgonda.routers.v1 import v1_router

# Ensure data directory exists
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

# FastAPI app initialization
app = FastAPI()
app.include_router(v1_router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
