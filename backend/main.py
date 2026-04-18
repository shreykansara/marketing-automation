from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routes import signals, leads, deals
from backend.core.db import init_db
from backend.core.logger import get_logger

logger = get_logger("main")

app = FastAPI(title="Blostem Intelligence Platform API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize DB on startup
@app.on_event("startup")
async def startup_event():
    init_db()
    logger.info("Application started and database initialized.")

# Include Routes
app.include_router(signals.router, prefix="/api/signals", tags=["Signals"])
app.include_router(leads.router, prefix="/api/leads", tags=["Leads"])
app.include_router(deals.router, prefix="/api/deals", tags=["Deads"])

@app.get("/")
async def root():
    return {"message": "Blostem Intelligence Platform API is online.", "version": "2.0"}
