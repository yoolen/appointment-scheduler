from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.rest.auth import router as auth_router

app = FastAPI(
    title="Appointment Scheduler API",
    description="Dual REST/GraphQL API for appointment scheduling",
    version="1.0.0",
)

# Add CORS middleware
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://localhost:3000",
    "https://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include REST API routers
app.include_router(auth_router)


@app.get("/")
async def root():
    return {
        "message": "Appointment Scheduler API",
        "endpoints": {"rest_docs": "/docs", "graphql": "/graphql", "health": "/health"},
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
