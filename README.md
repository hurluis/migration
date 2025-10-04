# 🏡 Plataforma de Reservas de Propiedades

Aplicación tipo Airbnb compuesta por un backend **FastAPI** y un conjunto de páginas HTML/CSS estáticas. El backend expone una API REST para gestionar usuarios, propiedades, reservas y feedback, persiste en SQLite o PostgreSQL y sirve los assets del frontend cuando se ejecuta localmente o dentro del contenedor.

## 🧱 Arquitectura

| Capa | Descripción |
| --- | --- |
| Backend | Servicio FastAPI (`backend/main.py`) con ORM ligero basado en SQLAlchemy, inicialización de tablas y sembrado automático de propiedades para sincronizarse con el frontend. |
| Frontend | Vistas estáticas (`frontend/*.html`) que consumen la API mediante `fetch`, se estilizan con TailwindCSS y se sirven con FastAPI o un contenedor Nginx. |
| Base de datos | SQLite por defecto (`backend/app.db`) o PostgreSQL si se define `DATABASE_URL`. |

## 📁 Estructura del repositorio

```
├── backend/
│   ├── Dockerfile                # Imagen utilizada por docker-compose
│   ├── main.py                   # Aplicación FastAPI con API REST y archivos estáticos
│   ├── requirements.txt          # Dependencias exactas del backend
│   └── static/                   # Recursos adicionales para el frontend
│
├── frontend/
│   ├── *.html                    # Vistas públicas, flujo de reserva y panel admin
│   ├── estilos/
│   │   ├── api.js                # Helper para resolver la URL base de la API
│   │   └── styles.css            # Hoja de estilos global
│   └── nginx.conf                # Configuración para servir las vistas con Nginx
│
├── docker-compose.yml            # Orquestación de backend, frontend y PostgreSQL
├── Dockerfile.backend            # Dockerfile alternativo legado
├── LICENSE.txt
├── main.py                       # Implementación previa del backend (referencia histórica)
└── requirements.txt              # Dependencias flexibles para desarrollo rápido
```

> ℹ️ El backend de referencia se encuentra en `backend/main.py`. El `main.py` de la raíz se conserva únicamente por compatibilidad con despliegues antiguos.

## 🧩 Funcionalidades del backend

- Autenticación simple: registro y login con almacenamiento de credenciales.
- Gestión de propiedades: catálogo precargado con cinco inmuebles y consultas desde el frontend.
- Reservas con validaciones: bloqueo de solapamientos, verificación de fechas futuras y actualización de estados vencidos mediante tareas en segundo plano.
- Historial del usuario: endpoints para reservas activas y pasadas.
- Feedback: envío y consulta de comentarios por propiedad.

## 🌐 Endpoints principales

Las rutas están disponibles tanto en `/` como con el prefijo `/api`.

| Método | Ruta | Descripción |
| ------ | ---- | ----------- |
| `POST` | `/register` | Crea un usuario y devuelve su `id`. |
| `POST` | `/login` | Valida credenciales y responde con el `user_id`. |
| `GET` | `/reserved-dates/{property_id}` | Lista fechas ocupadas para el calendario de reservas. |
| `POST` | `/reserve` | Crea una reserva si no hay solapamientos y la fecha es futura. |
| `GET` | `/active-reservations/{user_id}` | Obtiene reservas activas con detalles de la propiedad. |
| `GET` | `/update-reservations` | Actualiza en segundo plano las reservas expiradas. |
| `GET` | `/past-reservations/{user_id}` | Devuelve reservas históricas del usuario. |
| `POST` | `/cancel-reservation` | Cancela una reserva activa antes del check-in. |
| `POST` | `/feedback` | Almacena un comentario y calificación para una propiedad. |
| `GET` | `/feedback/{property_id}` | Recupera todos los comentarios asociados a la propiedad. |

## 🖥️ Ejecución local

1. **Crear y activar entorno virtual (opcional):**
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```
2. **Instalar dependencias del backend:**
   ```bash
   pip install -r backend/requirements.txt
   ```
3. **Configurar variables de entorno (si aplica):**
   - `DATABASE_URL`: cadena SQLAlchemy. Si no se define, se crea `backend/app.db` con SQLite.
   - `FRONTEND_DIR`: ruta alternativa al directorio `frontend/`.
   - Opcionalmente coloca estas claves en un archivo `.env`; `load_dotenv()` las leerá automáticamente.
4. **Inicializar y levantar FastAPI:**
   ```bash
   uvicorn backend.main:app --reload
   ```
5. **Abrir el frontend:**
   - `http://localhost:8000/` muestra la landing (`index.html`).
   - El backend sirve `/frontend`, `/estilos` y los archivos estáticos registrados.

Durante el primer arranque se crean las tablas necesarias y se insertan los registros iniciales de propiedades para mantener sincronizado el catálogo.

## 🐳 Despliegue con Docker Compose

- Imágenes públicas: https://hub.docker.com/repositories/hurluis

### Pasos rápidos para clonar y levantar los contenedores

1. Asegúrate de tener **Docker Desktop** abierto y en ejecución.
2. Clona el repositorio:
   ```bash
   git clone https://github.com/JULILYHERRERA/AIRBNB_GESTION.git
   ```
3. Entra a la carpeta del proyecto:
   ```bash
   cd AIRBNB_GESTION/migration
   ```
4. (Opcional) Define `DATABASE_URL` y otras credenciales en `.env` para que Compose las consuma.
5. Levanta los servicios:
   ```bash
   docker compose up --build
   ```
6. Accede a:
   - `http://localhost` para el frontend servido por Nginx.
   - `http://localhost:8000/docs` para la documentación interactiva.

Servicios incluidos en `docker-compose.yml`:
- **fastapi-backend**: ejecuta `backend/main.py`, monta el directorio `frontend/` como recursos estáticos y expone la API REST.
- **nginx-frontend**: entrega las páginas HTML precompiladas con la configuración de `frontend/nginx.conf`.
- **local-postgres-db**: instancia PostgreSQL 15 con volumen persistente `booking-postgres-data`.
