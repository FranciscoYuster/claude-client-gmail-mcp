# Gmail MCP - Instalación Automática y Segura

> Acceso de asistentes de IA a Gmail mediante el Model Context Protocol (MCP)

> **Requisito esencial:** Debes tener instalado [Claude Desktop](https://www.anthropic.com/claude/desktop) para poder utilizar este servidor MCP.

## 🧪 ¿Qué es MCP?

MCP (Model Context Protocol) es un protocolo de integración desarrollado por Antrophic para facilitar la comunicación entre modelos de lenguaje (como ChatGPT o Claude) y herramientas externas (APIs, bases de datos, servicios web, etc.). Su objetivo es proporcionar un contexto ampliado, estructurado y en tiempo real a los modelos, permitiéndoles ejecutar acciones más allá del texto.

---

## 🚀 Instalación rápida (Windows)

1. Primero:
   - Ve a [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
   - Crea un proyecto y habilita la API de Gmail
   - Agrega `http://localhost:8080/` a las **URIs de redireccionamiento autorizados**
   - Descarga el archivo `client_secret_...json` y déjalo en tu carpeta Descargas (no te preocupes por el nombre ni la ubicación final)
   - El instalador detectará y moverá el archivo automáticamente a la carpeta correcta y con el nombre adecuado
> [!IMPORTANT]
> Solo necesitas descargar el archivo de credenciales desde Google Cloud despues configurar las **URIs de redireccionamiento autorizadas** y dejarlo en Descargas. ¡No te preocupes por el nombre ni la ubicación final, el instalador se encarga de todo!
2. Clona este repositorio desde tu **terminal**:
   ```sh
   git clone https://github.com/FranciscoYuster/claude-client-gmail-mcp
   cd claude-client-gmail-mcp
   ```
3. Y ejecuta el script:
   ```sh
   python setup.py
   ```
4. El instalador hará el resto
5. Cuando veas el mensaje final, ¡abre Claude Desktop y disfruta!

---

## 💻 Instalación en macOS / Linux

1. Sigue los mismos pasos de Google Cloud indicados arriba para obtener tu archivo de credenciales y dejarlo en Descargas.
2. Clona este repositorio desde tu terminal:
   ```sh
   git clone https://github.com/FranciscoYuster/gmail-client-mcp-server
   cd gmail-client-mcp-server
   ```
3. Ejecuta el script para sistemas Unix:
   ```sh
   python3 setupUnix.py
   ```
4. El instalador hará el resto.
5. Cuando veas el mensaje final, ¡abre Claude Desktop y disfruta!

---

> [!IMPORTANT]
> Si usas **Windows**, ejecuta: `python setup.py`
> Si usas **macOS o Linux**, ejecuta: `python3 setupUnix.py`
> Ambos scripts ejecutan la instalación, pero cada uno está adaptado a su sistema operativo.

---

## 🔒 Seguridad

> [!WARNING]
> **Nunca subas ni compartas tu archivo de credenciales.** Si lo expones por error, elimínalo y genera uno nuevo en Google Cloud Console. El script nunca sube ni distribuye tus datos sensibles.

---

## 📝 Requisitos previos

- Python 3.11 o superior
- git
- Cuenta de Gmail
- Claude Dekstop

> [!TIP]
> El instalador te guiará para instalar cualquier requisito que falte.

---

## ⚙️ Configuración manual

### 🚀 Configuración

1. Clona este repositorio:
   ```sh
   git clone https://github.com/FranciscoYuster/claude-client-gmail-mcp
   cd claude-client-gmail-mcp
   ```
2. Crea y activa un entorno virtual:
   ```sh
   uv init
   # o alternativamente
   uv venv
   ```
   Luego actívalo:
   ```sh
   .venv\scripts\activate
   ```
3. Instala dependencias:
   ```sh
   uv pip install -r requirements.txt
   ```
4. Configura credenciales OAuth:
   - Crea un directorio llamado `credentials` en la raíz del proyecto
   - Crea un proyecto en [Google Cloud Console](https://console.cloud.google.com/)
   - Habilita la API de Gmail
   - Crea credenciales OAuth
   - Agrega la siguiente URI a las **URIs de redirección autorizadas**:
     ```
     http://localhost:8080/
     ```
   - Descarga el archivo JSON de credenciales y guárdalo como `credentials/client_secret_gmail_oauth.json`

> [!CAUTION]
> Asegúrate de que la ruta y el nombre del archivo de credenciales sean correctos para evitar errores de autenticación.

5. Agrega el servidor MCP a tu configuración JSON. Por favor, consulta la documentación oficial de tu cliente MCP para instrucciones específicas. Asegúrate de ajustar la ruta según tu entorno:
   ```json
   {
       "mcpServers": {
           "gmail-mcp": {
               "command": "uv",
               "args": [
                   "--directory",
                   "/path/to/your/gmail-mcp/src",
                   "run",
                   "main.py"
               ]
           }
       }
   }
   ```

6. Ejecuta Claude Desktop
---

## 📝 Licencia

MIT. Consulta el archivo [LICENSE](LICENSE).
