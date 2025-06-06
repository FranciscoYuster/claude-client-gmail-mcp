"""
herramientas.py - Definición de herramientas para operaciones de Gmail
Envío, borradores, lectura, búsqueda, modificación, eliminación y gestión de etiquetas, además de herramientas relacionadas con etiquetas.
"""
import base64
import json
from typing import Dict, Any, Tuple, List
from bs4 import BeautifulSoup

# Utilidades
from utils.label_manager import (
    create_label, update_label, delete_label,
    list_labels, find_label_by_name, get_or_create_label
)
import utils.gmail_utils as gmail_utils
from utils.utils import decode_base64url


# --- Herramientas: Operaciones de correo ---
async def send_email(args: Dict[str, Any]) -> str:
    """
    Envía un correo electrónico con los parámetros especificados.

    Args:
        args (Dict[str, Any]): Diccionario con las siguientes claves.
            - to (List[str]): Lista de destinatarios.
            - subject (str): Asunto del correo.
            - body (str): Cuerpo del mensaje.
            - cc (List[str], opcional): Lista de CC.
            - bcc (List[str], opcional): Lista de BCC.
            - in_reply_to (str, opcional): ID del mensaje al que se responde.
            - threadid (str, opcional): ID del hilo.

    Returns:
        str: Mensaje de resultado del envío (ejemplo: "Correo enviado: ID_MENSAJE").
    """
    msg = gmail_utils.create_email_message({
        "to": args["to"],                       # Lista de destinatarios
        "subject": args["subject"],             # Asunto
        "body": args["body"],                   # Cuerpo
        "cc": args.get("cc"),                   # CC (opcional)
        "bcc": args.get("bcc"),                 # BCC (opcional)
        "in_reply_to": args.get("in_reply_to"), # ID de mensaje al que se responde (opcional)
    }).encode("utf-8")
    # Codificar el mensaje en Base64
    raw = base64.urlsafe_b64encode(msg).decode().rstrip("=")
    # payload contiene los datos del mensaje
    payload: Dict[str, Any] = {"raw": raw}
    # Si se especifica threadid, se añade al payload
    if "threadid" in args:
        payload["threadId"] = args["threadid"]
    response = gmail_utils.service.users().messages().send(userId="me", body=payload).execute()
    return f"Correo enviado: {response['id']}"


async def create_draft(args: Dict[str, Any]) -> str:
    """
    Crea un borrador de correo electrónico con los parámetros especificados.

    Args:
        args (Dict[str, Any]): Diccionario con las siguientes claves.
            - to (List[str]): Lista de destinatarios.
            - subject (str): Asunto.
            - body (str): Cuerpo.
            - cc (List[str], opcional): Lista de CC.
            - bcc (List[str], opcional): Lista de BCC.
            - in_reply_to (str, opcional): ID del mensaje al que se responde.
            - threadid (str, opcional): ID del hilo.

    Returns:
        str: Mensaje de resultado de la creación del borrador (ejemplo: "Borrador creado: ID_BORRADOR").
    """
    msg = gmail_utils.create_email_message({
        "to": args["to"],
        "subject": args["subject"],
        "body": args["body"],
        "cc": args.get("cc"),
        "bcc": args.get("bcc"),
        "in_reply_to": args.get("in_reply_to"),
    }).encode("utf-8")
    raw = base64.urlsafe_b64encode(msg).decode().rstrip("=")
    # Crear el borrador
    draft = gmail_utils.service.users().drafts().create(
        userId="me", 
        body={"message": {"raw": raw, "threadId": args.get("threadid")}}
        ).execute()
    return f"Borrador creado: {draft.get('id')}"


async def read_email(args: Dict[str, Any]) -> str:
    """
    Obtiene un correo electrónico por ID y extrae su cuerpo.

    Args:
        args (Dict[str, Any]): Diccionario con las siguientes claves.
            - messageid (str): ID del mensaje a obtener.
            - htmlLimit (int, opcional): Máximo de caracteres HTML a devolver (por defecto 10,000).
            - htmlOffset (int, opcional): Offset de inicio para el HTML (por defecto 0).

    Returns:
        str: Cadena JSON con las claves:
            - text (str): Cuerpo en texto plano.
            - html (str): Fragmento HTML.
            - truncated (bool): Si el HTML fue truncado.
            - nextOffset (int o None): Siguiente offset, o None si se obtuvo todo el HTML.
    """
    # Obtener el mensaje
    msg = gmail_utils.service.users().messages().get(userId="me", id=args["messageid"], format="full").execute()

    def extract_email_body(part: Dict[str, Any]) -> Tuple[str, str]:
        """Extrae el cuerpo del correo electrónico"""
        text, html = "", ""

        if "data" in part.get("body", {}):
            # Decodifica el cuerpo del mensaje de Base64URL a UTF-8
            content = decode_base64url(part["body"]["data"])
            if part.get("mimeType") == "text/plain": text = content
            elif part.get("mimeType") == "text/html": 
                # Analiza el HTML y extrae solo los elementos principales
                soup = BeautifulSoup(content, "html.parser")
                main_texts = [p.get_text(strip=True) for p in soup.find_all(["p", "div"])]
                html = "\n".join(main_texts)

        for sub in part.get("parts", []):
            # El cuerpo puede estar anidado, se extrae recursivamente
            t, h = extract_email_body(sub); text += t; html += h
        return text, html
    
    text, html = extract_email_body(msg["payload"])

    # Opciones configurables por el cliente
    limit = args.get("htmlLimit", 10_000)  # Máximo de caracteres por fragmento
    offset = args.get("htmlOffset", 0)     # Desde qué carácter leer

    # Fragmentar el HTML
    html_chunks = html[offset: offset + limit] 
    truncated = len(html) > offset + limit

    return json.dumps({
        "text": text,
        "html": html_chunks,
        "truncated": truncated,  # Si hay más fragmentos
        "nextOffset": offset + limit if truncated else None
    }, ensure_ascii=False)


async def search_emails(args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Busca correos en Gmail y devuelve IDs y cabeceras.

    Args:
        args:
            - query (str, opcional): Consulta de búsqueda de Gmail (ejemplo: "is:unread newer_than:1d")
            - maxResults (int, opcional): Máximo de resultados (por defecto 10)
            - pageToken (str, opcional): Token para la siguiente página

    Returns:
        Dict[str, Any]: {
            "messages": [
                {
                    "id": <ID del mensaje>,
                    "threadId": <ID del hilo>,
                    "Subject": <Asunto>,
                    "From": <Remitente>,
                    "Date": <Fecha>
                },
                ...
            ],
            "nextPageToken": <str>  # None si no hay más páginas
        }
    """
    service = gmail_utils.service

    # Preparar argumentos
    query = args.get("query", "")
    max_results = args.get("maxResults", 10)
    page_token = args.get("pageToken")

    # Llamar a la API list
    list_params = {"userId": "me", "maxResults": max_results}
    if query:
        list_params["q"] = query
    if page_token:
        list_params["pageToken"] = page_token

    resp = service.users().messages().list(**list_params).execute()
    ids = [m["id"] for m in resp.get("messages", [])]
    next_token = resp.get("nextPageToken")

    # Obtener metadatos en lote
    results: List[Dict[str, Any]] = []
    if ids:
        batch = service.new_batch_http_request()
        def _collect(request_id, response, exception):
            if exception:
                # Si falla uno, se omite
                return
            hdrs = {h["name"]: h["value"] for h in response["payload"]["headers"]}
            results.append({
                "id": response["id"],
                "threadId": response.get("threadId"),
                "Subject": hdrs.get("Subject", ""),
                "From": hdrs.get("From", ""),
                "Date": hdrs.get("Date", ""),
            })

        for msg_id in ids:
            batch.add(
                service.users().messages().get(
                    userId="me",
                    id=msg_id,
                    format="metadata",
                    metadataHeaders=["Subject", "From", "Date"]
                ),
                callback=_collect
            )
        batch.execute()

    return {
        "messages": results,
        "nextPageToken": next_token
    }


async def delete_email(args: Dict[str, Any]) -> str:
    """
    Elimina un correo electrónico por su ID.

    Args:
        args (Dict[str, Any]):
            - messageid (str): ID del mensaje a eliminar.

    Returns:
        str: Mensaje de resultado de la eliminación (ejemplo: "Correo eliminado: ID_MENSAJE").
    """
    gmail_utils.service.users().messages().delete(userId="me", id=args["messageid"]).execute()
    return f"Correo eliminado: {args['messageid']}"


# --- Herramientas: Operaciones con etiquetas ---
async def modify_label(args: Dict[str, Any]) -> str:
    """
    Añade o elimina etiquetas de un correo electrónico por su ID.

    Args:
        args (Dict[str, Any]):
            - messageid (str): ID del mensaje.
            - addLabelIds (List[str], opcional): IDs de etiquetas a añadir.
            - removeLabelIds (List[str], opcional): IDs de etiquetas a eliminar.

    Returns:
        str: Mensaje de resultado de la operación.
    """
    body: Dict[str, Any] = {}
    # Solo se añaden los parámetros necesarios
    if "addLabelIds" in args: body["addLabelIds"] = args["addLabelIds"]
    if "removeLabelIds" in args: body["removeLabelIds"] = args["removeLabelIds"]
    # Modifica las etiquetas del mensaje
    gmail_utils.service.users().messages().modify(
        userId="me",
        id=args["messageid"],
        body=body
    ).execute()
    return f"Etiquetas modificadas: {args['messageid']}"


async def create_label_tool(args: Dict[str, Any]) -> str:
    """
    Crea una nueva etiqueta.

    Args:
        args (Dict[str, Any]):
            - name (str): Nombre de la etiqueta.
            - messageListVisibility (str, opcional): Visibilidad en la lista de mensajes.
            - labelListVisibility (str, opcional): Visibilidad en la lista de etiquetas.

    Returns:
        str: Mensaje de resultado de la creación.
    """
    lbl = create_label(
        gmail_utils.service,
        args["name"],
        args.get("messageListVisibility", "show"),
        args.get("labelListVisibility", "labelShow")
    )
    return f"Etiqueta creada: {lbl['id']}: {lbl['name']}"


async def delete_label_tool(args: Dict[str, Any]) -> str:
    """
    Elimina una etiqueta por su nombre.

    Args:
        args (Dict[str, Any]):
            - name (str): Nombre de la etiqueta a eliminar.

    Returns:
        str: Mensaje de resultado de la eliminación.
    """
    label = find_label_by_name(gmail_utils.service, args["name"])
    if not label:
        raise ValueError(f"Etiqueta '{args['name']}' no encontrada")
    
    result = delete_label(gmail_utils.service, label.id)
    return result["message"]


async def list_labels_tool() -> str:
    """
    Obtiene la lista de todas las etiquetas y la devuelve como texto.

    Args:
        Ninguno

    Returns:
        str: Lista de etiquetas (nombre, ID y tipo) separadas por salto de línea.
    """
    lbls = list_labels(gmail_utils.service)
    lines = [f"{l['name']} (ID: {l['id']}), Tipo: {l['type']}" for l in lbls["all"]]
    return "\n".join(lines)


async def get_or_create_label_tool(args: Dict[str, Any]) -> str:
    """
    Obtiene una etiqueta por nombre o la crea si no existe.

    Args:
        args (Dict[str, Any]):
            - name (str): Nombre de la etiqueta.
            - messageListVisibility (str, opcional)
            - labelListVisibility (str, opcional)

    Returns:
        str: Mensaje de preparación de la etiqueta.
    """
    lbl = get_or_create_label(
        gmail_utils.service, args["name"],
        args.get("messageListVisibility", "show"),
        args.get("labelListVisibility", "labelShow")
    )
    return f"Etiqueta lista: {lbl.id}: {lbl.name}"


async def update_label_tool(args: Dict[str, Any]) -> str:
    """
    Actualiza la configuración de una etiqueta.

    Busca la etiqueta por nombre y actualiza los siguientes atributos:
    - name: Nombre de la etiqueta (obligatorio)
    - messageListVisibility: Visibilidad en la lista de mensajes ("show" / "hide")
    - labelListVisibility: Visibilidad en la lista de etiquetas ("labelShow" / "labelHide" / "labelShowIfUnread")
    - color: Configuración de color (dict con textColor y backgroundColor)
        - backgroundColor: 
            #ac2b16, #cc3a21, #eaa041, #f2c960, #16a766, #43d692,
            #3c78d8, #4986e7, #8e63ce, #b99aff, #f691b2, #e07798,
            #616161, #a4c2f4, #d0bcf1, #fbc8d9, #f6c5be, #e4d7f5,
            #fad165, #fef1d1, #c6f3de, #a0eac9, #c9daf8, #b3efd3
        - textColor: 
            #ffffff, #000000

    Args:
        args (Dict[str, Any]):
            - name (str): Nombre de la etiqueta a actualizar.
            - updates (Dict[str, Any]): Diccionario con los cambios.
    """
    # 1) Desanidar si es necesario
    params = args.get("args", args)

    # 2) Comprobar campo obligatorio
    name = params.get("name")
    if not name:
        raise ValueError("Falta el argumento obligatorio: 'name'")

    label = find_label_by_name(gmail_utils.service, name)
    if not label:
        raise ValueError(f"Etiqueta '{name}' no encontrada")
    label_id = label.id

    # 3) Obtener updates
    raw_updates = params.get("updates")
    if not isinstance(raw_updates, dict):
        raise ValueError("Falta o es inválido el argumento 'updates'")

    # 4) Claves permitidas
    allowed_top = {"name", "messageListVisibility", "labelListVisibility", "color"}
    allowed_backgrounds = {
        "#ac2b16","#cc3a21","#eaa041","#f2c960","#16a766","#43d692",
        "#3c78d8","#4986e7","#8e63ce","#b99aff","#f691b2","#e07798",
        "#616161","#a4c2f4","#d0bcf1","#fbc8d9","#f6c5be","#e4d7f5",
        "#fad165","#fef1d1","#c6f3de","#a0eac9","#c9daf8","#b3efd3"
    }
    allowed_texts = {"#ffffff", "#000000"}

    updates: Dict[str, Any] = {}
    for k, v in raw_updates.items():
        if k not in allowed_top:
            continue
        if k == "color":
            if not isinstance(v, dict):
                continue
            color_updates: Dict[str, str] = {}
            if "textColor" in v:
                if v["textColor"] not in allowed_texts:
                    raise ValueError(f"textColor inválido: {v['textColor']}")
                color_updates["textColor"] = v["textColor"]
            if "backgroundColor" in v:
                if v["backgroundColor"] not in allowed_backgrounds:
                    raise ValueError(f"backgroundColor inválido: {v['backgroundColor']}")
                color_updates["backgroundColor"] = v["backgroundColor"]
            if color_updates:
                updates["color"] = color_updates
        else:
            updates[k] = v

    if not updates:
        raise ValueError("No se proporcionaron campos válidos para actualizar")

    # 5) Realizar la actualización
    try:
        updated = update_label(gmail_utils.service, label_id, updates)
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise RuntimeError(f"Fallo update_label. updates={updates!r}, error={e!r}")

    name_display = updated.get("name") or label.name
    return f"Etiqueta actualizada: {updated.get('id', 'unknown')}: {name_display}"


async def find_label_by_name_tool(args: Dict[str, Any]) -> str:
    """
    Busca una etiqueta por nombre.

    Args:
        args (Dict[str, Any]):
            - name (str): Nombre de la etiqueta a buscar.

    Returns:
        str: Mensaje de resultado de la búsqueda.
    """
    lbl = find_label_by_name(gmail_utils.service, args["name"])
    return f"Etiqueta encontrada: {lbl.id}: {lbl.name}"