from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import uvicorn
import os
import time
from dotenv import load_dotenv

from routes.resume import router as resume_router
from routes.interview import router as interview_router
from routes.job import router as job_router
from routes.analytics import router as analytics_router
from routes.report import router as report_router
from firebase_config import initialize_firebase
from utils.logger import log_request, log_response, log_error, log_system_event
from utils.exceptions import handle_exception

# Load environment variables
load_dotenv()

app = FastAPI(
    title="HireReady AI API",
    description="AI-powered mock interview system backend",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
        "http://localhost:3002",
        "http://127.0.0.1:3002",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Firebase
try:
    firebase_ready = initialize_firebase()
    if firebase_ready:
        print("Firebase initialized successfully")
        log_system_event("Firebase initialized successfully")
    else:
        print("Firebase not initialized; continuing in local/mock mode")
        log_system_event("Firebase not initialized; continuing in local/mock mode")
except Exception as e:
    print(f"Firebase initialization failed: {e}")
    print("Continuing without Firebase...")
    log_error(e, "Firebase initialization")

# Include routers
app.include_router(resume_router, prefix="/api/resume", tags=["Resume"])
app.include_router(interview_router, prefix="/api/interview", tags=["Interview"])
app.include_router(job_router, prefix="/api/job", tags=["Job"])
app.include_router(analytics_router, prefix="/api/analytics", tags=["Analytics"])
app.include_router(report_router, prefix="/api/report", tags=["Report"])

# Create local directories
os.makedirs("uploads", exist_ok=True)
os.makedirs("logs", exist_ok=True)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests and responses."""
    start_time = time.time()
    user_id = request.headers.get("X-User-ID")
    log_request(request.method, str(request.url.path), user_id)

    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        log_response(request.method, str(request.url.path), response.status_code, process_time)
        response.headers["X-Process-Time"] = str(process_time)
        return response
    except Exception as e:
        log_error(e, f"Request failed: {request.method} {request.url.path}")
        http_exception = handle_exception(e)
        return JSONResponse(
            status_code=http_exception.status_code,
            content=http_exception.detail
        )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler."""
    log_error(exc, f"Unhandled exception in {request.method} {request.url.path}")
    http_exception = handle_exception(exc)
    return JSONResponse(
        status_code=http_exception.status_code,
        content=http_exception.detail
    )


if not os.path.exists("uploads"):
    os.makedirs("uploads")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "HireReady AI API is running",
        "version": "1.0.0",
        "status": "healthy"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "version": "1.0.0"
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
