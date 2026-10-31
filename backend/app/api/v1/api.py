from fastapi import APIRouter
from app.api.v1.auth import router as auth_router
from app.api.v1.profile import router as profile_router
from app.api.v1.resumes import router as resumes_router
from app.api.v1.jobs import router as jobs_router
from app.api.v1.risk import router as risk_router
from app.api.v1.match import router as match_router
from app.api.v1.saved_jobs import router as saved_jobs_router
from app.api.v1.applications import router as applications_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(profile_router)
api_router.include_router(resumes_router)
api_router.include_router(jobs_router)
api_router.include_router(risk_router)
api_router.include_router(match_router)
api_router.include_router(saved_jobs_router)
api_router.include_router(applications_router)
