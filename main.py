"""
FastAPI main application
"""
import os
from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

from backend.routes import clients, holdings, orders
from backend.config import APP_TITLE, APP_VERSION, AUTHORIZED_USERS

# Environment detection
# HF Spaces provides SPACE_ID (e.g., "username/space-name")
IS_PRODUCTION = os.getenv("SPACE_ID") is not None
SPACE_ID = os.getenv("SPACE_ID", "")

# Construct Space URL from SPACE_ID if in production
# SPACE_ID format: "username/space-name"
# Space URL format: "https://username-space-name.hf.space"
if IS_PRODUCTION and SPACE_ID:
    SPACE_HOST = f"https://{SPACE_ID.replace('/', '-')}.hf.space"
else:
    SPACE_HOST = ""

# Session Cookie Name
SESSION_COOKIE_NAME = "dashboard_session"

# Create FastAPI app
app = FastAPI(
    title=APP_TITLE,
    version=APP_VERSION,
    description="Trading Dashboard API with Dhan Integration"
)

# Configure CORS based on environment
if IS_PRODUCTION and SPACE_HOST:
    # In production, use specific origin
    allowed_origins = [SPACE_HOST, SPACE_HOST.rstrip("/")]
    print(f"🚀 Production mode detected")
    print(f"   Space ID: {SPACE_ID}")
    print(f"   Space URL: {SPACE_HOST}")
    print(f"   Allowed origins: {allowed_origins}")
else:
    # In development, allow all origins
    allowed_origins = ["*"]
    print("Development mode detected. Allowing all origins.")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class LoginRequest(BaseModel):
    username: str
    password: str

import logging
logger = logging.getLogger("uvicorn")

# Middleware for authentication
@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    # Public paths that don't require auth
    public_paths = ["/login", "/api/login", "/static", "/health"]
    
    path = request.url.path
    
    # Allow access to public paths
    if any(path.startswith(p) for p in public_paths) or path == "/favicon.ico":
        return await call_next(request)
    
    # Check for session cookie
    session = request.cookies.get(SESSION_COOKIE_NAME)
    logger.info(f"Auth: path={path}, session={session}")
    
    if not session:
        # If it's an API request, return 401
        if path.startswith("/api/"):
            logger.warning(f"Auth: Unauthorized API request to {path}")
            return Response(content='{"detail": "Unauthorized"}', status_code=401, media_type="application/json")
        
        # Otherwise redirect to login page with the current path as "next"
        logger.info(f"Auth: Redirecting {path} to /login")
        return RedirectResponse(url=f"/login?next={path}")
    
    return await call_next(request)

# Include routers
app.include_router(clients.router)
app.include_router(holdings.router)
app.include_router(orders.router)

# Mount static files
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")

# Serve UI pages
@app.get("/login")
async def login_page():
    return FileResponse("frontend/login.html")

@app.get("/")
async def root():
    # Auth is handled by middleware
    return FileResponse("frontend/index.html")
    
@app.get("/new")
async def root():
    # Auth is handled by middleware
    return FileResponse("frontend/index.html")
    
@app.get("/holdings")
async def holdings_page():
    return FileResponse("frontend/holdings.html")

@app.get("/place-order")
async def place_order_page():
    return FileResponse("frontend/place-order.html")

@app.get("/account-details")
async def account_details_page():
    return FileResponse("frontend/account-details.html")

# Authentication API endpoints
@app.post("/api/login", status_code=200)
async def login(login_data: LoginRequest, response: Response):
    user = login_data.username
    password = login_data.password
    
    if user in AUTHORIZED_USERS and AUTHORIZED_USERS[user] == password:
        # Set a session cookie with environment-appropriate settings
        logger.info(f"✅ Login success: {user} (Production: {IS_PRODUCTION})")
        
        # Cookie settings based on environment
        cookie_config = {
            "key": SESSION_COOKIE_NAME,
            "value": user,
            "httponly": True,
            "max_age": 3600 * 24,  # 24 hours
            "path": "/",
            "samesite": "none" if IS_PRODUCTION else "lax",
        }
        
        # Only set secure flag in production (HTTPS)
        if IS_PRODUCTION:
            cookie_config["secure"] = True
            logger.info(f"🔒 Setting secure cookie for production")
        else:
            logger.info(f"🔓 Setting non-secure cookie for development")
        
        response.set_cookie(**cookie_config)
        
        # Add headers to help with cookie propagation in HF Spaces
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        
        logger.info(f"🍪 Cookie set with config: {cookie_config}")
        logger.info(f"📤 Response headers: {dict(response.headers)}")
        
        return {"status": "success", "username": user}
    
    logger.warning(f"❌ Login failed for user: {user}")
    raise HTTPException(status_code=401, detail="Invalid username or password")


@app.get("/api/user/me")
async def get_current_user(request: Request):
    user = request.cookies.get(SESSION_COOKIE_NAME)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return {"username": user}

@app.get("/api/logout")
async def logout(response: Response):
    # Delete cookie with same settings as when it was set
    cookie_config = {
        "key": SESSION_COOKIE_NAME,
        "path": "/",
        "samesite": "none" if IS_PRODUCTION else "lax"
    }
    
    if IS_PRODUCTION:
        cookie_config["secure"] = True
    
    response.delete_cookie(**cookie_config)
    logger.info("🚪 User logged out")
    return RedirectResponse(url="/login")


# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "app": APP_TITLE, "version": APP_VERSION}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True, reload_dirs=["backend", "frontend"])

