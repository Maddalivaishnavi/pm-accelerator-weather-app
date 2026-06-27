"""
Entry point. Run with:
    uvicorn app.main:app --reload
"""
from dotenv import load_dotenv
load_dotenv()  # must run before app.services.ai_insights reads env vars

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.routers import weather, records

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Weather App API",
    description=(
        "Backend for the PM Accelerator AI Engineer Intern technical assessment. "
        "Built by [YOUR NAME HERE]."
    ),
    version="1.0.0",
)

# Wide-open CORS since this is a local dev assessment project, not production.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(weather.router)
app.include_router(records.router)


@app.get("/")
def root():
    return {
        "status": "ok",
        "docs": "/docs",
        "endpoints": ["/api/weather/lookup", "/api/weather/by-coordinates", "/api/records"],
    }


@app.get("/api/about")
def about():
    """PM Accelerator description, surfaced via the API per the assessment's
    requirement that the app include info about PM Accelerator."""
    return {
        "developer": "MADDALI VAISHNAVI",
        "about_pm_accelerator": (
            "The Product Manager Accelerator Program is designed to support PM "
            "professionals through every stage of their careers. From students "
            "looking for entry-level jobs to Directors looking to take on a "
            "leadership role, our program has helped hundreds of students fulfill "
            "their career aspirations. Our Product Manager Accelerator community "
            "are ambitious and committed — through our program they have learnt, "
            "honed, and developed new PM and leadership skills, giving them a "
            "strong foundation for their future endeavors. Learn more at "
            "https://www.pmaccelerator.io/"
        ),
    }
