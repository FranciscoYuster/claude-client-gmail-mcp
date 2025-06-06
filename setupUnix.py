import os
import sys
import subprocess
import json
import shutil

# Paso 1: Verificar si uv está instalado
def check_uv():
    print("\U0001F4E6 Verificando si 'uv' está instalado...")
    result = subprocess.run(['which', 'uv'], capture_output=True, text=True)
    if result.returncode != 0:
        print("\U0001F504 'uv' no está instalado. Instalando...")
        install_cmd = [
            'sh', '-c', 'curl -Ls https://astral.sh/uv/install.sh | sh'
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
    home = os.path.expanduser('~')
    # macOS: ~/Library/Application Support/Claude/claude_desktop_config.json
    # Linux: ~/.config/Claude/claude_desktop_config.json
    mac_path = os.path.join(home, 'Library', 'Application Support', 'Claude', 'claude_desktop_config.json')
    linux_path = os.path.join(home, '.config', 'Claude', 'claude_desktop_config.json')
    if os.path.exists(mac_path):
        return mac_path
    elif os.path.exists(linux_path):
        return linux_path
    else:
        print('❌ No se encontró el archivo de configuración de Claude Desktop.')
        print('Asegúrate de haber iniciado Claude Desktop al menos una vez.')
        sys.exit(1)

def insert_config():
    config_path = get_claude_config_path()
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
    repo_url = "https://github.com/FranciscoYuster/gmail-client-mcp-server"
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
        subprocess.run(['open', 'https://www.python.org/downloads/release/python-3110/'])
        sys.exit(1)
    else:
        print(f"🐍 Python {sys.version.split()[0]} detectado.")

def check_git():
    print("🔎 Verificando si git está instalado...")
    result = subprocess.run(['git', '--version'], capture_output=True, text=True)
    if result.returncode != 0:
        print("❌ 'git' no está instalado o no está en el PATH. Descargando instalador...")
        subprocess.run(['open', 'https://git-scm.com/download/mac'])
        sys.exit(1)
    else:
        print(f"Git instalado✔️ {result.stdout.strip()}")

def check_credentials():
    cred_dir = os.path.join(os.getcwd(), 'credentials')
    downloads_dir = os.path.join(os.path.expanduser('~'), 'Downloads')
    if not os.path.exists(cred_dir):
        os.makedirs(cred_dir)
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
        subprocess.run(['open', 'https://console.cloud.google.com/apis/credentials'])
        sys.exit(1)
    else:
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
