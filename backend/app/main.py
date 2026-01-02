from .crud import init_db
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
import os
import logging

# Logic Imports
from .database import engine, Base
from . import main_api 

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("cv_api")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create DB Tables on startup if missing
    Base.metadata.create_all(bind=engine)
    init_db.sync_templates(db)
    yield

app = FastAPI(title="AI CV Builder", lifespan=lifespan)

# --- CORS FIX ---
# Instead of "*", we list the exact URLs of your frontend
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True, 
    allow_methods=["*"],
    allow_headers=["*"],
)
# ----------------

# ROUTER: Connect the corrected API
app.include_router(main_api.router, prefix="/api")

# STATIC FILES: Support for Production Build (Optional)
frontend_path = os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "dist")
if os.path.exists(frontend_path):
    app.mount("/assets", StaticFiles(directory=os.path.join(frontend_path, "assets")), name="assets")
    @app.get("/{full_path:path}")
    async def serve_react(full_path: str):
        if full_path.startswith("api"): return {"error": "Not Found"}
        target = os.path.join(frontend_path, full_path)
        if os.path.exists(target) and os.path.isfile(target): return FileResponse(target)
        return FileResponse(os.path.join(frontend_path, "index.html"))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)