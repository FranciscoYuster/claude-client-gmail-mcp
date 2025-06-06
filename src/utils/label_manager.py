from typing import List, Optional, Dict, Any
from dataclasses import dataclass

from googleapiclient.discovery import Resource
from googleapiclient.errors import HttpError


@dataclass
class LabelColor:
    """
    Clase de datos que representa la configuración de color de una etiqueta de Gmail.

    Atributos:
        textColor: Color del texto del nombre de la etiqueta (código CSS)
        backgroundColor: Color de fondo de la etiqueta (código CSS)
    """
    textColor: Optional[str] = None
    backgroundColor: Optional[str] = None


@dataclass
class GmailLabel:
    """
    Clase de datos para un objeto Label de la API de Gmail.

    Atributos:
        id: ID único de la etiqueta
        name: Nombre de la etiqueta
        type: "system" o definida por el usuario
        messageListVisibility: Visibilidad en la lista de mensajes
        labelListVisibility: Visibilidad en la lista de etiquetas
        messagesTotal: Total de mensajes
        messagesUnread: Mensajes no leídos
        color: Configuración de color de la etiqueta
    """
    id: str
    name: str
    type: Optional[str] = None
    messageListVisibility: Optional[str] = None
    labelListVisibility: Optional[str] = None
    messagesTotal: Optional[int] = None
    messagesUnread: Optional[int] = None
    color: Optional[LabelColor] = None


def create_label(service: Resource,
                 label_name: str,
                 message_list_visibility: str = "show",
                 label_list_visibility: str = "labelshow") -> Dict[str, Any]:
    """
    Crea una nueva etiqueta con el nombre especificado.

    Args:
        service: Objeto Resource de la API de Google
        label_name: Nombre de la etiqueta a crear
        message_list_visibility: Visibilidad en la lista de mensajes
        label_list_visibility: Visibilidad en la lista de etiquetas

    Returns:
        Dict[str, Any]: Información de la etiqueta creada
    """
    body = {
        "name": label_name,
        "messageListVisibility": message_list_visibility,
        "labelListVisibility": label_list_visibility,
    }

    try:
        label = service.users().labels().create(userId="me", body=body).execute()
        return label
    except HttpError as error:
        msg = getattr(error, "error_details", str(error))
        if "already exists" in msg:
            raise ValueError(f"La etiqueta '{label_name}' ya existe")
        raise ValueError(f"No se pudo crear la etiqueta: {msg}")


def update_label(service: Resource,
                 label_id: str,
                 updates: Dict[str, Any]) -> Dict[str, Any]:
    """
    Actualiza los atributos de una etiqueta especificada.

    Args:
        service: Objeto Resource de la API de Google
        label_id: ID de la etiqueta a actualizar
        updates: Diccionario con los atributos a actualizar

    Returns:
        Dict[str, Any]: Información de la etiqueta actualizada
    """
    try:
        service.users().labels().get(userId="me", id=label_id).execute()
        response = service.users().labels().update(
            userId="me", id=label_id, body=updates
        ).execute()
        return response
    except HttpError as error:
        if error.status_code == 404:
            raise ValueError(f"Etiqueta con ID '{label_id}' no encontrada")
        raise ValueError(f"No se pudo actualizar la etiqueta: {error}")


def delete_label(service: Resource, label_id: str) -> Dict[str, Any]:
    """
    Elimina una etiqueta especificada (no se pueden eliminar etiquetas del sistema).

    Args:
        service: Objeto Resource de la API de Google
        label_id: ID de la etiqueta a eliminar

    Returns:
        Dict[str, Any]: Información de la etiqueta eliminada
    """
    try:
        data = service.users().labels().get(userId="me", id=label_id).execute()
        if data.get("type") == "system":
            raise ValueError(f"No se puede eliminar la etiqueta del sistema '{label_id}'")
        service.users().labels().delete(userId="me", id=label_id).execute()
        return {"success": True, "message": f"Etiqueta '{data.get('name')}' eliminada correctamente"}
    except HttpError as error:
        if error.status_code == 404:
            raise ValueError(f"Etiqueta con ID '{label_id}' no encontrada")
        raise ValueError(f"No se pudo eliminar la etiqueta: {error}")


def list_labels(service: Resource) -> Dict[str, Any]:
    """
    Obtiene todas las etiquetas y las clasifica en sistema/usuario.

    Args:
        service: Objeto Resource de la API de Google

    Returns:
        Dict[str, Any]: Listado de etiquetas
    """
    try: 
        resp = service.users().labels().list(userId="me").execute()
        labels = resp.get("labels", [])
        system = [lbl for lbl in labels if lbl.get("type") == "system"]
        user = [lbl for lbl in labels if lbl.get("type") == "user"]
        return {
            "all": labels,
            "system": system,
            "user": user,
            "count": {
                "total": len(labels),
                "system": len(system),
                "user": len(user),
            },
        }
    except HttpError as error:
        raise ValueError(f"No se pudo listar las etiquetas: {error}")


def find_label_by_name(service: Resource, label_name: str) -> Optional[GmailLabel]:
    """
    Busca una etiqueta por nombre y devuelve una instancia de GmailLabel si la encuentra (no distingue mayúsculas/minúsculas).
    Si no la encuentra, devuelve None.

    Args:
        service: Objeto Resource de la API de Google
        label_name: Nombre de la etiqueta a buscar

    Returns:
        Optional[GmailLabel]: Instancia de la etiqueta encontrada o None
    """
    raw = list_labels(service)["all"]
    for data in raw:
        if data.get("name", "").lower() == label_name.lower():
            color_data = data.get("color", {})
            color = LabelColor(
                textColor=color_data.get("textColor"),
                backgroundColor=color_data.get("backgroundColor"),
            ) if color_data else None
            return GmailLabel(
                id=data.get("id"),
                name=data["name"],
                type=data.get("type"),
                messageListVisibility=data.get("messageListVisibility"),
                labelListVisibility=data.get("labelListVisibility"),
                messagesTotal=data.get("messagesTotal"),
                messagesUnread=data.get("messagesUnread"),
                color=color,
            )
    return None


def get_or_create_label(service: Resource,
                        label_name: str,
                        message_list_visibility: str = "show",
                        label_list_visibility: str = "labelshow" ) -> GmailLabel:
    """
    Crea una nueva etiqueta con el nombre especificado o la devuelve si ya existe.

    Args:
        service: Objeto Resource de la API de Google
        label_name: Nombre de la etiqueta
        message_list_visibility: Visibilidad en la lista de mensajes
        label_list_visibility: Visibilidad en la lista de etiquetas

    Returns:
        GmailLabel: Instancia de la etiqueta
    """
    existing = find_label_by_name(service, label_name)
    if existing:
        return existing
    raw = create_label(service, label_name, message_list_visibility, label_list_visibility)
    color_data = raw.get("color", {})
    color = LabelColor(
        textColor=color_data.get("textColor"),
        backgroundColor=color_data.get("backgroundColor"),
    ) if color_data else None
    return GmailLabel(
        id=raw.get("id"),
        name=raw.get("name"),
        type=raw.get("type"),
        messageListVisibility=raw.get("messageListVisibility"),
        labelListVisibility=raw.get("labelListVisibility"),
        messagesTotal=raw.get("messagesTotal"),
        messagesUnread=raw.get("messagesUnread"),
        color=color,
    )
