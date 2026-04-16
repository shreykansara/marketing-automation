from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import deals, signals, leads, companies
from services.signal_engine.scheduler import start_scheduler, shutdown_scheduler

app = FastAPI(title="Blostem Pipeline Intelligence")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Since it's MVP
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
