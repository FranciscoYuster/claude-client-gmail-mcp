import os
import sys
import subprocess
import json
import shutil

# Paso 1: Verificar si uv está instalado
def check_uv():
    print("\U0001F4E6 Verificando si 'uv' está instalado...")
    result = subprocess.run(['where', 'uv'], capture_output=True, text=True, shell=True)
    if result.returncode != 0:
        print("\U0001F504 'uv' no está instalado. Instalando...")
        install_cmd = [
            'powershell',
            '-Command',
            'iwr https://astral.sh/uv/install.ps1 -UseBasicParsing | iex'
        ]
        subprocess.run(install_cmd, check=True)
    else:
        print("'uv' ya está instalado.")

# Paso 2: Crear entorno virtual
def create_venv():
    print("\U0001F527 Inicializando entorno virtual...")
    subprocess.run(['uv', 'venv'], check=True)

# Paso 3: Instalar dependencias
def install_deps():
    print("\U0001F4DA Instalando dependencias...")
    subprocess.run(['uv', 'pip', 'install', '-r', 'requirements.txt'], check=True)

# Paso 4: Insertar configuración en Claude Desktop
def get_claude_config_path():
    userprofile = os.environ.get('USERPROFILE')
    if not userprofile:
        print('❌ No se pudo determinar la variable USERPROFILE.')
        sys.exit(1)
    return os.path.join(userprofile, 'AppData', 'Roaming', 'Claude', 'claude_desktop_config.json')

def insert_config():
    config_path = get_claude_config_path()
    if not os.path.exists(config_path):
        print(f'❌ No se encontró el archivo de configuración de Claude Desktop en:\n   {config_path}')
        print('Asegúrate de haber iniciado Claude Desktop al menos una vez.')
        sys.exit(1)
    print('🛠️ Insertando configuración en claude_desktop_config.json...')
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    if 'mcpServers' not in config:
        config['mcpServers'] = {}
    current_dir = os.path.abspath(os.getcwd())
    config['mcpServers']['gmail-mcp'] = {
        'command': 'uv',
        'args': ['--directory', current_dir, 'run', 'src/main.py']
    }
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    print(f'✅ Configuración insertada correctamente en:\n   {config_path}')

# Paso 5: Mensaje final
def final_message():
    print("\n🚀 Instalación completa. Ahora abre Claude Desktop.\n")

def clonar_repo_si_no_existe():
    # Nota: Para clonar una rama específica de GitHub, se usa la URL base del repo y el flag '-b <rama>'.
    # No se debe usar la URL con '/tree/dev', solo la base.
    repo_url = "https://github.com/FranciscoYuster/claude-client-gmail-mcp"
    destino = os.path.join(os.getcwd(), "gmail-mcp-server")
    if not os.path.exists(destino):
        print("🔄 Clonando el repositorio (rama 'dev')...")
        subprocess.run(["git", "clone", "-b", "dev", repo_url, destino], check=True)
        print("✅ Repositorio clonado en:", destino)
    else:
        print("📁 El repositorio ya existe en:", destino)
    os.chdir(destino)

def check_python_version():
    print("🔎 Verificando si python está instalado...")
    if sys.version_info < (3, 11):
        print('❌ Python 3.11 o superior es requerido. Versión detectada:', sys.version)
        print('🔄 Abriendo página de descarga de Python 3.11...')
        subprocess.run(['start', 'https://www.python.org/downloads/release/python-3110/'], shell=True)
        sys.exit(1)
    else:
        print(f"🐍 Python {sys.version.split()[0]} detectado.")

def check_git():
    print("🔎 Verificando si git está instalado...")
    result = subprocess.run(['git', '--version'], capture_output=True, text=True, shell=True)
    if result.returncode != 0:
        print("❌ 'git' no está instalado o no está en el PATH. Descargando instalador...")
        subprocess.run(['start', 'https://git-scm.com/download/win'], shell=True)
        sys.exit(1)
    else:
        print(f"Git instalado✔️ {result.stdout.strip()}")

def check_credentials():
    cred_dir = os.path.join(os.getcwd(), 'credentials')
    downloads_dir = os.path.join(os.path.expanduser('~'), 'Downloads')
    if not os.path.exists(cred_dir):
        os.makedirs(cred_dir)
    # Buscar cualquier archivo que empiece por 'client_secret' y termine en '.json' en Descargas
    cred_file = None
    for fname in os.listdir(downloads_dir):
        if fname.startswith('client_secret') and fname.endswith('.json'):
            cred_file = os.path.join(downloads_dir, fname)
            break
    if not cred_file:
        print('❌ No se encontró el archivo de credenciales en Descargas: client_secret_...json')
        print('🔗 Abriendo Google Cloud Console para que generes tus credenciales OAuth...')
        print('1. Ve a https://console.cloud.google.com/apis/credentials')
        print('2. Crea un proyecto y habilita la API de Gmail')
        print('3. Agrega "http://localhost:8080/" a las URIs de redireccionamiento autorizados')
        print('4. Descarga el archivo client_secret_...json y déjalo en tu carpeta Descargas')
        subprocess.run(['start', 'https://console.cloud.google.com/apis/credentials'], shell=True)
        sys.exit(1)
    else:
        # Copiar el archivo a credentials/client_secret_gmail_oauth.json
        destino = os.path.join(cred_dir, 'client_secret_gmail_oauth.json')
        shutil.copy2(cred_file, destino)
        print(f'✔️ Archivo de credenciales copiado desde Descargas y renombrado a credentials/client_secret_gmail_oauth.json')

def main():
    check_python_version()
    check_git()
    clonar_repo_si_no_existe()
    check_credentials()
    check_uv()
    create_venv()
    install_deps()
    insert_config()
    final_message()

if __name__ == '__main__':
    main()
