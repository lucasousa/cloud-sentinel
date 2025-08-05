import os
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from starlette.responses import RedirectResponse

from src.integrations import patch_all_integrations


@asynccontextmanager
async def lifespan(app: FastAPI):
    await patch_all_integrations()
    yield


def create_app():
    app = FastAPI(lifespan=lifespan)

    @app.get("/")
    async def index():
        return RedirectResponse(url="/")

    return app


app_ = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("src.main:app_", host="0.0.0.0", port=port, reload=True)
