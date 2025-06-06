import re
import os
import base64
from typing import List, Dict, Any, Optional

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build, Resource


service: Optional[Resource] = None

def load_credentials(config_path: str, cred_path: str, oauth_path: str, scopes: List[str]) -> None:
    """
    Lee/actualiza las credenciales OAuth2.0 e inicializa el cliente de la API de Gmail.
    """
    # exist_ok=True: Si el directorio no existe, lo crea. Si es False y no existe, lanza error.
    os.makedirs(config_path, exist_ok=True)
    creds = None
    if os.path.exists(cred_path):
        try:
            # Lee el archivo credentials.json y crea el objeto Credentials para Google API
            creds = Credentials.from_authorized_user_file(cred_path, scopes)
        except ValueError:
            os.remove(cred_path)
            creds = None
    if not creds or not creds.valid:
        # Si no hay token o está expirado, crea uno nuevo
        if creds and creds.expired and creds.refresh_token:
            # Si hay refresh_token, refresca
            creds.refresh(Request())
        else:
            # Si no hay refresh_token, realiza autenticación interactiva
            flow = InstalledAppFlow.from_client_secrets_file(oauth_path, scopes)
            creds = flow.run_local_server(port=8080, access_type='offline', prompt='consent')
        with open(cred_path, "w") as token:
            token.write(creds.to_json())
    global service
    service = build("gmail", "v1", credentials=creds)


def encode_email_header(text: str) -> str:
    """
    Codifica cabeceras con caracteres no ASCII en Base64 según RFC2047.
    """
    # Verifica si hay caracteres no ASCII
    if re.search(r'[^\x00-\x7F]', text):
        # Codifica en Base64
        encoded = base64.b64encode(text.encode('utf-8')).decode('utf-8')
        # Devuelve la cabecera en formato RFC2047
        return f"=?UTF-8?b?{encoded}?="
    return text


def validate_email(email: str) -> bool:
    """
    Valida el formato de una dirección de correo con una expresión regular simple.
    No es una validación exhaustiva, pero cubre lo básico.
    """
    email_regex = re.compile(r'^[^\s@]+@[^\s@]+\.[^\s@]+$')
    return bool(email_regex.match(email))


def create_email_message(args: Dict[str, Any]) -> str:
    """
    Construye un mensaje MIME de texto plano a partir de los datos recibidos.

    Claves de args:
        - from: Remitente (str)
        - to: Lista de destinatarios (List[str])
        - cc: Lista de CC (opcional)
        - bcc: Lista de BCC (opcional)
        - in_reply_to: ID del mensaje al que se responde (opcional)
        - subject: Asunto (str)
        - body: Cuerpo (str)

    return:
        - Mensaje MIME en texto plano (str)
    """
    # Codifica el asunto
    subject = encode_email_header(args.get("subject", ""))

    # Valida los destinatarios
    to_list: List[str] = args.get("to", [])
    for addr in to_list:
        if not validate_email(addr):
            raise ValueError(f"Dirección de correo inválida: {addr}")

    # Construye las cabeceras
    headers: List[str] = []
    headers.append(f"From: {args.get('from', 'me')}")
    headers.append(f"To: {', '.join(to_list)}")
    if args.get("cc"):
        headers.append(f"Cc: {', '.join(args['cc'])}")
    if args.get("bcc"):
        headers.append(f"Bcc: {', '.join(args['bcc'])}")
    headers.append(f"Subject: {subject}")
    if args.get("in_reply_to"):
        headers.append(f"In-Reply-To: {args['in_reply_to']}")
        headers.append(f"References: {args['in_reply_to']}")
    headers.append("MIME-Version: 1.0")
    headers.append("Content-Type: text/plain; charset=UTF-8")
    headers.append("Content-Transfer-Encoding: 7bit")

    # Une cabeceras y cuerpo
    message = "\r\n".join(headers) + "\r\n\r\n" + args.get("body", "")
    return message

