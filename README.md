# 🏡 Plataforma de Reservas de Propiedades

Este proyecto es una plataforma web tipo Airbnb desarrollada con **HTML**, **CSS**, **FastAPI** y **Supabase**, que permite a los usuarios explorar propiedades en alquiler, ver detalles, realizar reservas con validación, y dejar retroalimentación para futuros usuarios.

## 📁 Estructura del Proyecto

```
├── page.HTML             # Página principal con listado de propiedades
├── detalle.html          # Detalles individuales de cada propiedad
├── reserva.html          # Formulario para completar la reserva
├── reserva-bef.html      # Página previa a la reserva
├── Mis-reservas.html     # Historial de reservas del usuario
├── feedback.html         # Sección para comentarios y retroalimentación
├── styles.css            # Estilos personalizados
├── main.py               # Backend con FastAPI (gestión de lógica del sistema)
```

## 🚀 Características Principales

- 🎯 **Explorar Propiedades**: Visualiza propiedades con imagen, precio y ubicación.
- 📍 **Detalles Ampliados**: Imágenes grandes, mapa embebido y más información.
- ✅ **Validación de Usuarios**: Inicio de sesión, registro y autenticación con Supabase.
- 📆 **Reservas Inteligentes**: Guarda y bloquea fechas ya reservadas.
- 💬 **Retroalimentación**: Usuarios pueden dejar comentarios útiles sobre los alojamientos y calificaciones.
- 🔐 **Gestión de Reservas**: Visualización desde “Mis reservas”.
- ☁️ **Base de Datos en la Nube**: Usando Supabase para guardar usuarios, reservas y feedbacks.
- 🔄 **Actualización Asíncrona**: Background tasks y respuestas rápidas vía FastAPI.

## 🛠️ Tecnologías Usadas

- **Frontend**: HTML5, CSS3
- **Backend**: [FastAPI](https://fastapi.tiangolo.com/)
- **Base de Datos**: [Supabase](https://supabase.com/) (PostgreSQL + Auth + Storage)
- **Autenticación**: Supabase Auth
- **Entorno**: Python 3.11+, dotenv, Pydantic
- **Servidor estático (Docker)**: nginx:alpine (por ahora solo FRONTEND)


## ▶️ Cómo Ejecutarlo
1. Instala las dependencias:
   ```bash
   pip install fastapi "uvicorn[standard]" python-dotenv supabase
   ```

2. Configura tus variables de entorno en un archivo `.env`:
   ```env
   SUPABASE_URL=https://tuproyecto.supabase.co
   SUPABASE_KEY=tu_clave_secreta
   ```

3. Ejecuta el servidor:
   ```bash
   uvicorn main:app --reload
   ```

4. Abre el navegador en:
   ```
   http://localhost:8000
   ```

## 📌 Mejoras Futuras

- Búsqueda y filtrado avanzado de propiedades.
- Panel administrativo para propietarios.
- Notificaciones por correo o SMS.


## frontend con Docker (Nginx)

**Requisitos**
-Docker Desktop (Windows/Mac) o Docker Engine (Linux)

1-Construir la imagen

Ubícate en la carpeta raíz del repo (donde existe la carpeta frontend/) y ejecuta:

   ```bash
   cd frontend
   docker build -t airbnb-frontend .
   ```

2-Ejecutar el contenedor

   ```bash
   docker run -d --name airbnb-frontend -p 8080:80 airbnb-frontend
   ```

4. Abre el navegador en:
   ```
   http://localhost:8080
   ```

**Actualizar imagen tras cambios**

   ```bash
   docker rm -f airbnb-frontend
   docker build -t airbnb-frontend ./frontend
   docker run -d --name airbnb-frontend -p 8080:80 airbnb-frontend
   ```