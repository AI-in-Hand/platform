import logging

from fastapi import FastAPI
from routers.v1 import v1_router

from nalgonda.constants import DATA_DIR

# Ensure directories exist
DATA_DIR.mkdir(exist_ok=True)

app = FastAPI()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        # logging.FileHandler(DATA_DIR / "logs.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

app.include_router(v1_router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
