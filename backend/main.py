import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
import traceback

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

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    error_msg = "".join(traceback.format_exception(None, exc, exc.__traceback__))
    print(f"--- GLOBAL ERROR CAUGHT ---\n{error_msg}\n---------------------------")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error", "error_type": str(type(exc).__name__), "message": str(exc)},
    )

app.add_middleware(
    CORSMiddleware,
    # Allow .vercel.app, .github.io, and localhost origins specifically to support credentials
    allow_origin_regex=r"https://mail\.google\.com|https://.*\.vercel\.app|https://.*\.github\.io|http://localhost(:\d+)?|chrome-extension://.*",
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
