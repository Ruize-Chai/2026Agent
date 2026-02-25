
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Oriflow Minimal API")


class HealthResponse(BaseModel):
	status: str
	version: str | None = None


@app.get("/", response_model=HealthResponse)
async def root():
	return {"status": "ok", "version": None}


@app.get("/health", response_model=HealthResponse)
async def health():
	return {"status": "healthy", "version": None}


if __name__ == "__main__":
	import uvicorn

	uvicorn.run(app, host="127.0.0.1", port=8000)
