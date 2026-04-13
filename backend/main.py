from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import deals

app = FastAPI(title="Blostem Pipeline Intelligence")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Since it's MVP
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(deals.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
