import gradio as gr
import os
import hashlib
from modules.auth import load_auth_data, auth_list_to_dict
import modules.constants as constants
from modules.ui_gradio_extensions import webpath

def create_login_page():
    """
    Creates a custom login page for Fooocus.
    Returns the login interface and a function to check credentials.
    """
    auth_dict = load_auth_data(constants.AUTH_FILENAME)
    login_css_path = webpath('css/login.css')
    custom_css = f'<link rel="stylesheet" href="{login_css_path}">'
    
    with gr.Blocks(title="Fooocus Login", css=custom_css) as login_page:
        # Background div
        gr.HTML('<div class="login-background"></div>')
        
        with gr.Row():
            with gr.Column(scale=1):
                pass
            with gr.Column(scale=2):
                with gr.Box(elem_classes="login-container"):
                    # Text-based logo
                    gr.HTML('<div class="login-logo"><h1 style="font-size: 42px; font-weight: bold; margin: 0; background: linear-gradient(90deg, #3b82f6, #8b5cf6); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">Fooocus</h1></div>')
                    
                    # Header
                    with gr.Group(elem_classes="login-header"):
                        gr.Markdown("# Fooocus Login")
                        gr.Markdown("Please enter your credentials to access Fooocus")
                    
                    # Form
                    with gr.Group(elem_classes="login-form"):
                        username = gr.Textbox(label="Username", placeholder="Enter your username")
                        password = gr.Textbox(label="Password", placeholder="Enter your password", type="password")
                        login_error = gr.HTML(elem_id="login_error", elem_classes="login-error", visible=False)
                        
                        login_btn = gr.Button("Login", variant="primary", elem_classes="login-button")
                
                def check_credentials(username, password):
                    if not username or not password:
                        return {login_error: gr.update(value="Please enter both username and password", visible=True)}
                    
                    if username not in auth_dict:
                        return {login_error: gr.update(value="Invalid username or password", visible=True)}
                    
                    password_hash = hashlib.sha256(bytes(password, encoding='utf-8')).hexdigest()
                    if password_hash != auth_dict[username]:
                        return {login_error: gr.update(value="Invalid username or password", visible=True)}
                    
                    # Import here to avoid circular imports
                    from modules.custom_auth import create_session, set_auth_cookie
                    
                    # Create a session and set cookie
                    session_id = create_session(username)
                    
                    # Return success message
                    return {login_error: gr.update(value='<span style="color:green">Login successful! Redirecting...</span>', visible=True)}
                
                def redirect_after_login():
                    return """
                    <script>
                        setTimeout(() => {
                            window.location.href = '/?__theme=' + (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
                        }, 1000);
                    </script>
                    """
                
                login_btn.click(
                    fn=check_credentials,
                    inputs=[username, password],
                    outputs=[login_error]
                ).success(
                    fn=redirect_after_login,
                    inputs=[],
                    outputs=[login_error]
                )
            
            with gr.Column(scale=1):
                pass
    
    return login_page

def is_authenticated(request):
    """
    Check if the current request is authenticated.
    This function will be used to determine whether to show the login page or the main UI.
    """
    # Extract auth header
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return False
    
    # Parse auth header
    try:
        auth_type, auth_value = auth_header.split(" ", 1)
        if auth_type.lower() != "basic":
            return False
        
        import base64
        decoded = base64.b64decode(auth_value).decode("utf-8")
        username, password = decoded.split(":", 1)
        
        # Check credentials
        auth_dict = load_auth_data(constants.AUTH_FILENAME)
        if username not in auth_dict:
            return False
        
        password_hash = hashlib.sha256(bytes(password, encoding='utf-8')).hexdigest()
        return password_hash == auth_dict[username]
    except:
        return False 