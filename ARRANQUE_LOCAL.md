# Guía de Arranque en Local (Backend & Frontend)

Instrucciones para levantar los servicios de `server` (FastAPI) y `web` (Next.js) en tu entorno local.

---

## 🐍 1. Backend (`server` - FastAPI)

Abre una terminal PowerShell y navega a la carpeta `server`:

```powershell
cd server
```

### Paso 1: Configurar variables de entorno (solo la primera vez)
```powershell
# Si no tienes .env creado, copia la plantilla:
Copy-Item .env.template .env
```

### Paso 2: Activar entorno virtual e instalar dependencias
```powershell
# Activar el venv
.\venv\Scripts\Activate.ps1

# (Opcional) Si agregas nuevas librerías:
pip install -r requirements.txt
```

### Paso 3: Arrancar el servidor FastAPI
```powershell
uvicorn app.main:app --reload --port 8000
```

* **API Base:** [http://localhost:8000](http://localhost:8000)
* **Documentación interactiva (Swagger UI):** [http://localhost:8000/docs](http://localhost:8000/docs)
* **OpenAPI Schema (JSON):** [http://localhost:8000/openapi.json](http://localhost:8000/openapi.json)

---

## ⚛️ 2. Frontend (`web` - Next.js)

Abre otra terminal (PowerShell o CMD) y navega a la carpeta `web`:

```powershell
cd web
```

### Paso 1: Configurar variables de entorno (solo la primera vez)
```powershell
Copy-Item .env.template .env.local
```

### Paso 2: Instalar dependencias (solo la primera vez o tras cambios)
```powershell
npm install
# o si usas pnpm:
# pnpm install
```

### Paso 3: Arrancar en modo desarrollo
```powershell
npm run dev
# o si usas pnpm:
# pnpm dev
```

* **Aplicación Web:** [http://localhost:3000](http://localhost:3000)

---

## ⚡ Resumen Rápido (Dos Terminales)

| Terminal | Directorio | Comando de arranque | URL |
| :--- | :--- | :--- | :--- |
| **Terminal 1 (Backend)** | `server/` | `uvicorn app.main:app --reload --port 8000` | [http://localhost:8000/docs](http://localhost:8000/docs) |
| **Terminal 2 (Frontend)** | `web/` | `npm run dev` | [http://localhost:3000](http://localhost:3000) |

