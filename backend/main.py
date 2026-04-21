import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

# Load .env from ROOT
load_dotenv(os.path.join(os.path.dirname(__file__), '../.env'))

from backend.routes import signals, leads, deals, emails, companies, auth
from backend.core.db import init_db
from backend.core.logger import get_logger

logger = get_logger("main")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    init_db()
    logger.info("Application started and database initialized.")
    yield
    # Shutdown logic
    logger.info("Application shutting down...")

app = FastAPI(
    title="Blostem Intelligence Platform API",
    description="Refactored Sales Intelligence API for Signals, Leads, and Deals.",
    version="2.1",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routes
app.include_router(signals.router, prefix="/api/signals", tags=["Signals"])
app.include_router(leads.router, prefix="/api/leads", tags=["Leads"])
app.include_router(deals.router, prefix="/api/deals", tags=["Deals"])
app.include_router(emails.router, prefix="/api/emails", tags=["Emails"])
app.include_router(companies.router, prefix="/api/companies", tags=["Companies"])
app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])

@app.get("/")
async def root():
    return {"message": "Blostem Intelligence Platform API (No-Celery Edition) is online.", "version": "2.1"}
