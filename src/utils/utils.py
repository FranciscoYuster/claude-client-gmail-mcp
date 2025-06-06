import base64

def decode_base64url(data: str) -> str:
    """
    Convierte una cadena en formato Base64URL a una cadena UTF-8.

    En la API de Gmail y JWT, el formato Base64URL suele omitir los signos de igual (=) de padding.
    Esta función añade el padding necesario automáticamente para decodificar de forma segura.

    Args:
        data (str): Cadena en formato Base64URL posiblemente sin padding

    Returns:
        str: Cadena decodificada en UTF-8 (por ejemplo, el cuerpo de un correo)

    Raises:
        UnicodeDecodeError: Si el resultado no es válido como UTF-8
        binascii.Error: Si la entrada no es válida como Base64
    """
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + padding).decode("utf-8")