"""
server.py - Configuración e inicialización del servidor MCP de Gmail
"""
import os
from pathlib import Path

from mcp.server.fastmcp import FastMCP
import utils.gmail_utils as gmail_utils
from tools import (
    send_email, create_draft, read_email, search_emails, 
    modify_label, create_label_tool, delete_label_tool, list_labels_tool,
    get_or_create_label_tool, update_label_tool, find_label_by_name_tool,
    download_attachments, get_thread, mark_as_read, mark_as_unread, mark_as_important, mark_as_not_important
)

# Configuración
BASE_DIR = Path(__file__).resolve().parent.parent
CREDENTIALS_DIR = BASE_DIR / "credentials"
OAUTH_KEYS = os.getenv("GMAIL_OAUTH_PATH", str(CREDENTIALS_DIR / "client_secret_gmail_oauth.json"))
CRED_PATH = os.getenv("GMAIL_CREDENTIALS_PATH", str(CREDENTIALS_DIR / "credentials.json"))
SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]

def create_server() -> FastMCP:
    """Crea el servidor MCP y registra las herramientas"""
    server = FastMCP("gmail", version="1.0.1")
    
    # Registro de herramientas
    server.tool()(send_email)
    server.tool()(create_draft)
    server.tool()(read_email)
    server.tool()(search_emails)
    server.tool()(modify_label)
    server.tool()(create_label_tool)
    server.tool()(delete_label_tool)
    server.tool()(list_labels_tool)
    server.tool()(get_or_create_label_tool)
    server.tool()(update_label_tool)
    server.tool()(find_label_by_name_tool)
    server.tool()(download_attachments)
    server.tool()(get_thread)
    server.tool()(mark_as_read)
    server.tool()(mark_as_unread)
    server.tool()(mark_as_important)
    server.tool()(mark_as_not_important)
    
    return server

def init_gmail_credentials():
    """Realiza la autenticación de Gmail"""
    gmail_utils.load_credentials(
        config_path=BASE_DIR,
        cred_path=CRED_PATH,
        oauth_path=OAUTH_KEYS,
        scopes=SCOPES
    )