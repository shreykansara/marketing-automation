import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
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

# Custom CORS middleware to ensure headers are always present
@app.middleware("http")
async def custom_cors_middleware(request: Request, call_next):
    origin = request.headers.get("origin")
    
    # Handle preflight (OPTIONS) requests
    if request.method == "OPTIONS":
        response = await call_next(request)
        if origin:
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Credentials"] = "true"
            response.headers["Access-Control-Allow-Methods"] = "*"
            response.headers["Access-Control-Allow-Headers"] = "*"
        return response

    response = await call_next(request)
    
    if origin:
        # We allow localhost, vercel, and gmail/extensions
        allowed_patterns = [
            "localhost", "127.0.0.1", "vercel.app", 
            "chrome-extension://", "mail.google.com"
        ]
        if any(p in origin for p in allowed_patterns):
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Credentials"] = "true"
            
    return response

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "https://marketing-automation-xtd2.vercel.app",
        "https://marketing-automation-git-main-shreyhiralkansara-7751s-projects.vercel.app",
        "https://mail.google.com",
        "http://mail.google.com",
    ],
    allow_origin_regex=r"(chrome-extension://.*|https://.*\.vercel\.app)",
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
