from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routers import items

app = FastAPI(
    title="OSRS GE Portfolio API",
    description="API for OSRS Grand Exchange portfolio management and item tracking",
    version="1.0.0",
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(items.router, prefix="/api")


@app.get("/")
def root():
    return {
        "message": "OSRS GE Portfolio API",
        "docs": "/docs",
        "version": "1.0.0",
    }


@app.get("/health")
def health():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "api.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
