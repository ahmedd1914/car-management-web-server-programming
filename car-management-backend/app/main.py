from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import cars, garages, maintenance
from app.models.database import Base, engine

# Initialize the database
Base.metadata.create_all(bind=engine)

# Create the FastAPI app
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Allow requests from the frontend
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allow all headers
)

# Include Routers
app.include_router(cars.router)
app.include_router(garages.router)
app.include_router(maintenance.router)

@app.get("/")
def root():
    return {"message": "Welcome to the Car Management API!"}
