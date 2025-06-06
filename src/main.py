"""
main.py - Punto de entrada del Servidor MCP de Gmail
"""
from dotenv import load_dotenv

from server import create_server, init_gmail_credentials

# Carga de variables de entorno
load_dotenv()

def main():
    """Función principal de ejecución"""
    # Autenticación de Gmail
    init_gmail_credentials()
    
    # Crear servidor
    server = create_server()
    
    # Iniciar servidor
    print("[INFO] Iniciando el servidor MCP de Gmail...")
    server.run(transport="stdio")

if __name__ == "__main__":
    main()