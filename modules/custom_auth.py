import gradio as gr
import os
import hashlib
import time
import uuid
import json
from modules.auth import load_auth_data
import modules.constants as constants
from modules.login_page import create_login_page, is_authenticated

# Store sessions in memory (in a production environment, this should be a database)
sessions = {}

def generate_session_id():
    """Generate a unique session ID"""
    return str(uuid.uuid4())

def set_auth_cookie(session_id):
    """Create a cookie setting function for Gradio"""
    def set_cookie():
        # Set cookie to expire in 24 hours
        expiry = time.time() + 86400
        return {
            "js": f"""
                document.cookie = "fooocus_session_id={session_id}; path=/; expires={time.strftime('%a, %d %b %Y %H:%M:%S GMT', time.gmtime(expiry))}; SameSite=Strict";
                window.location.href = "/";
            """
        }
    return set_cookie

def get_auth_cookie(request):
    """Extract the session ID from cookies"""
    cookies = request.cookies
    return cookies.get("fooocus_session_id")

def validate_session(session_id):
    """Check if the session ID is valid"""
    if not session_id:
        return False
    
    session = sessions.get(session_id)
    if not session:
        return False
    
    # Check if session is expired
    if session.get("expires_at", 0) < time.time():
        del sessions[session_id]
        return False
    
    return True

def create_session(username):
    """Create a new session for the user"""
    session_id = generate_session_id()
    sessions[session_id] = {
        "username": username,
        "created_at": time.time(),
        "expires_at": time.time() + 86400  # 24 hours
    }
    return session_id

def auth_middleware(app):
    """
    Set up authentication middleware for the Gradio app.
    Returns the login interface.
    """
    # Create the login interface
    login_interface = create_login_page()
    
    # Create a route for the login page
    @app.route("/login", methods=["GET"])
    def login_route():
        return login_interface.render()
    
    # Add middleware for authentication
    @app.middleware("http")
    async def auth_middleware_handler(request, call_next):
        # Skip authentication for static files and the login page itself
        path = request.url.path
        if path.startswith("/file=") or path.startswith("/static/") or path == "/login":
            return await call_next(request)
        
        # Check if user is already authenticated via session
        session_id = get_auth_cookie(request)
        if validate_session(session_id):
            return await call_next(request)
        
        # Check if user is authenticated via basic auth
        if is_authenticated(request):
            # Create a session for the user from basic auth
            auth_header = request.headers.get("Authorization")
            if auth_header:
                import base64
                auth_type, auth_value = auth_header.split(" ", 1)
                decoded = base64.b64decode(auth_value).decode("utf-8")
                username, _ = decoded.split(":", 1)
                create_session(username)
            return await call_next(request)
        
        # If not authenticated, redirect to login page
        from starlette.responses import RedirectResponse
        return RedirectResponse(url="/login")
    
    return login_interface 