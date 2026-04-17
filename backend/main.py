from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import deals, signals, leads, companies, outreach
from services.signal_engine.scheduler import start_scheduler, shutdown_scheduler

app = FastAPI(title="Blostem Pipeline Intelligence")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow all for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.on_event("startup")
def startup_event():
    start_scheduler()

@app.on_event("shutdown")
def shutdown_event():
    shutdown_scheduler()

app.include_router(deals.router)
app.include_router(signals.router)
app.include_router(leads.router)
app.include_router(companies.router)
app.include_router(outreach.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
