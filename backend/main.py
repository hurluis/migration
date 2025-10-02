# python -m uvicorn main:app --reload

from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, FastAPI, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from dotenv import load_dotenv
from datetime import date, datetime, timedelta
import os

# Nuevas importaciones para PostgreSQL
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent

frontend_dir_env = os.getenv("FRONTEND_DIR")
if frontend_dir_env:
    FRONTEND_DIR = Path(frontend_dir_env).resolve()
else:
    candidate = (BASE_DIR / "frontend").resolve()
    if not candidate.exists():
        candidate = (BASE_DIR.parent / "frontend").resolve()
    FRONTEND_DIR = candidate

if not FRONTEND_DIR.exists():
    raise RuntimeError(f"Frontend directory '{FRONTEND_DIR}' does not exist")

app = FastAPI()
app.mount('/static', StaticFiles(directory=BASE_DIR / "static"), name="static")
app.mount('/estilos', StaticFiles(directory=FRONTEND_DIR / "estilos"), name="estilos")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuración de la conexión a la base de datos local
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    DATABASE_URL = f"sqlite:///{BASE_DIR / 'app.db'}"

engine_kwargs = {}
if DATABASE_URL.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, **engine_kwargs)
IS_SQLITE = engine.url.get_backend_name() == "sqlite"

if IS_SQLITE:
    from sqlalchemy import event

    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


def init_db():
    """Crea las tablas necesarias si no existen."""
    if IS_SQLITE:
        ddl_statements = [
            """
            CREATE TABLE IF NOT EXISTS "Users" (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(255) NOT NULL,
                email VARCHAR(255) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS "Property" (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(255) NOT NULL,
                location TEXT,
                price NUMERIC(10, 2),
                description TEXT,
                image_url TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS "Bookings" (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                property_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                in_time DATE NOT NULL,
                out_time DATE NOT NULL,
                status VARCHAR(50) DEFAULT 'activo',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(property_id) REFERENCES "Property"(id) ON DELETE CASCADE,
                FOREIGN KEY(user_id) REFERENCES "Users"(id) ON DELETE CASCADE
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS "Feedback" (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_property INTEGER NOT NULL,
                comment TEXT NOT NULL,
                rating INTEGER CHECK (rating BETWEEN 1 AND 5),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(id_property) REFERENCES "Property"(id) ON DELETE CASCADE
            )
            """
        ]
    else:
        ddl_statements = [
            """
            CREATE TABLE IF NOT EXISTS "Users" (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                email VARCHAR(255) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT NOW()
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS "Property" (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                location TEXT,
                price NUMERIC(10, 2),
                description TEXT,
                image_url TEXT,
                created_at TIMESTAMP DEFAULT NOW()
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS "Bookings" (
                id SERIAL PRIMARY KEY,
                property_id INTEGER NOT NULL REFERENCES "Property"(id) ON DELETE CASCADE,
                user_id INTEGER NOT NULL REFERENCES "Users"(id) ON DELETE CASCADE,
                in_time DATE NOT NULL,
                out_time DATE NOT NULL,
                status VARCHAR(50) DEFAULT 'activo',
                created_at TIMESTAMP DEFAULT NOW()
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS "Feedback" (
                id SERIAL PRIMARY KEY,
                id_property INTEGER NOT NULL REFERENCES "Property"(id) ON DELETE CASCADE,
                comment TEXT NOT NULL,
                rating INTEGER CHECK (rating BETWEEN 1 AND 5),
                created_at TIMESTAMP DEFAULT NOW()
            )
            """
        ]

    with engine.begin() as connection:
        for ddl in ddl_statements:
            connection.execute(text(ddl))


init_db()

# --- Modelos Pydantic (sin cambios) ---
class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str

class FeedbackRequest(BaseModel):
    id_property: int
    comment: str
    rating: int
    
class LoginRequest(BaseModel):
    email: str
    password: str

class ReservationRequest(BaseModel):
    property_id: int
    user_id: int
    in_time: str
    out_time: str

# --- Funciones de ayuda para la base de datos ---
def execute_query(query, params=None):
    with engine.connect() as connection:
        try:
            result = connection.execute(text(query), params or {})
            connection.commit() # Importante para INSERT, UPDATE, DELETE
            return result
        except SQLAlchemyError as e:
            print(f"Error en la base de datos: {e}")
            raise HTTPException(status_code=500, detail="Error en la base de datos")

# --- Endpoints ---

api_router = APIRouter()


@app.get("/")
def home():
    return FileResponse(FRONTEND_DIR / "index.html")


@app.get("/{page_name}.html")
def serve_html_page(page_name: str):
    """Devuelve archivos HTML estáticos del frontend.

    Permite navegar directamente a rutas como ``/detalle.html`` sin
    depender de un servidor externo y evita interferir con las rutas de la API,
    ya que solo intercepta solicitudes que terminan en ``.html``.
    """

    target_file = (FRONTEND_DIR / f"{page_name}.html").resolve()

    try:
        target_file.relative_to(FRONTEND_DIR)
    except ValueError:
        raise HTTPException(status_code=404, detail="Página no encontrada")

    if not target_file.exists():
        raise HTTPException(status_code=404, detail="Página no encontrada")

    return FileResponse(target_file)


@api_router.post("/register")
async def register(user: RegisterRequest):
    # Verificar si el usuario ya existe
    query_check = 'SELECT * FROM "Users" WHERE email = :email'
    existing_user = execute_query(query_check, {"email": user.email}).first()
    if existing_user:
        return JSONResponse(content={"message": "El usuario ya existe"}, status_code=400)

    # Insertar nuevo usuario
    if IS_SQLITE:
        query_insert = 'INSERT INTO "Users" (name, email, password) VALUES (:name, :email, :password)'
        result = execute_query(query_insert, user.dict())
        user_id = result.lastrowid
    else:
        query_insert = 'INSERT INTO "Users" (name, email, password) VALUES (:name, :email, :password) RETURNING id'
        result = execute_query(query_insert, user.dict())
        user_id = result.scalar()

    return JSONResponse(content={"message": "Usuario registrado con éxito", "user_id": user_id}, status_code=201)


@api_router.post("/login")
async def login(user: LoginRequest):
    query = 'SELECT * FROM "Users" WHERE email = :email AND password = :password'
    result = execute_query(query, user.dict()).first()
    
    if not result:
        return JSONResponse(content={"message": "Correo o contraseña incorrectos"}, status_code=400)
    
    user_data = result._asdict()
    return JSONResponse(content={"message": "Inicio de sesión exitoso", "user_id": user_data['id']}, status_code=200)

def ensure_date(value):
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        try:
            return datetime.strptime(value, "%Y-%m-%d").date()
        except ValueError:
            return datetime.fromisoformat(value).date()
    raise ValueError("Formato de fecha desconocido")


@api_router.get("/reserved-dates/{property_id}")
async def get_reserved_dates(property_id: int):
    query = 'SELECT in_time, out_time FROM "Bookings" WHERE property_id = :property_id'
    bookings = execute_query(query, {"property_id": property_id}).fetchall()

    reserved_dates = []
    for booking in bookings:
        in_time = ensure_date(booking[0])
        out_time = ensure_date(booking[1])

        current_date = in_time
        while current_date <= out_time:
            reserved_dates.append(current_date.strftime("%Y-%m-%d"))
            current_date += timedelta(days=1)
    
    return JSONResponse(content={"reserved_dates": reserved_dates}, status_code=200)

@api_router.post("/reserve")
async def reserve(reservation: ReservationRequest):
    try:
        in_time = datetime.strptime(reservation.in_time, "%Y-%m-%d")
        out_time = datetime.strptime(reservation.out_time, "%Y-%m-%d")
    except ValueError:
        return JSONResponse(content={"message": "Formato de fecha inválido. Use YYYY-MM-DD"}, status_code=400)

    if in_time.date() < datetime.now().date():
        return JSONResponse(content={"message": "No puedes reservar fechas pasadas"}, status_code=400)

    # Comprobar si hay reservas que se solapan
    # Una reserva se solapa si (start1 <= end2) and (end1 >= start2)
    query_check = """
        SELECT id FROM "Bookings"
        WHERE property_id = :property_id AND
        in_time <= :out_time AND out_time >= :in_time
    """
    existing_reservation = execute_query(
        query_check,
        {"property_id": reservation.property_id, "in_time": in_time, "out_time": out_time},
    ).first()
    if existing_reservation:
        return JSONResponse(content={"message": "La propiedad ya está reservada en esas fechas"}, status_code=400)

    # Crear la nueva reserva
    query_insert = """
        INSERT INTO "Bookings" (property_id, user_id, in_time, out_time, status)
        VALUES (:property_id, :user_id, :in_time, :out_time, 'activo')
    """
    execute_query(query_insert, {
        "property_id": reservation.property_id,
        "user_id": reservation.user_id,
        "in_time": in_time,
        "out_time": out_time
    })

    return JSONResponse(content={"message": "Reserva realizada con éxito"}, status_code=201)

@api_router.get("/active-reservations/{user_id}")
async def get_active_reservations(user_id: int):
    now = datetime.now()
    # Usamos JOIN para obtener el nombre de la propiedad en una sola consulta
    query = """
        SELECT b.id, b.property_id, p.name AS property_name, b.in_time, b.out_time, b.status
        FROM "Bookings" b
        JOIN "Property" p ON b.property_id = p.id
        WHERE b.user_id = :user_id AND b.out_time >= :now
    """
    reservations = execute_query(query, {"user_id": user_id, "now": now}).fetchall()
    
    active_reservations = [row._asdict() for row in reservations]
    
    return JSONResponse(content={"reservations": active_reservations}, status_code=200)

async def update_expired_reservations():
    now = datetime.now()
    query = 'UPDATE "Bookings" SET status = \'terminado\' WHERE status = \'activo\' AND out_time < :now'
    execute_query(query, {"now": now})
    print("Reservas caducadas actualizadas.")

@api_router.get("/update-reservations")
async def trigger_update_reservations(background_tasks: BackgroundTasks):
    background_tasks.add_task(update_expired_reservations)
    return {"message": "Actualización de reservas caducadas iniciada"}

@api_router.get("/past-reservations/{user_id}")
async def get_past_reservations(user_id: int):
    now = datetime.now()
    query = """
        SELECT b.id, b.property_id, p.name AS property_name, b.in_time, b.out_time, b.status
        FROM "Bookings" b
        JOIN "Property" p ON b.property_id = p.id
        WHERE b.user_id = :user_id AND b.out_time < :now
    """
    reservations = execute_query(query, {"user_id": user_id, "now": now}).fetchall()
    
    past_reservations = [row._asdict() for row in reservations]

    return JSONResponse(content={"reservations": past_reservations}, status_code=200)

@api_router.post("/feedback")
async def submit_feedback(feedback: FeedbackRequest):
    # La consulta se actualiza para que coincida con la tabla
    query = """
        INSERT INTO "Feedback" (id_property, comment, rating)
        VALUES (:id_property, :comment, :rating)
    """
    execute_query(query, feedback.dict())
    return JSONResponse(content={"message": "Feedback guardado"}, status_code=201)
    
@api_router.get("/feedback/{property_id}")
async def get_feedback(property_id: int):
    query = 'SELECT * FROM "Feedback" WHERE id_property = :property_id'
    feedback_list = [row._asdict() for row in execute_query(query, {"property_id": property_id}).fetchall()]
    return JSONResponse(content={"feedback": feedback_list}, status_code=200)


app.include_router(api_router)
app.include_router(api_router, prefix="/api")
