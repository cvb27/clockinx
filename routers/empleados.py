import json
import os
from fastapi import APIRouter, Request, Form, Path, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
import csv
from datetime import datetime, time

router = APIRouter()
templates = Jinja2Templates(directory="templates")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ARCHIVO_USUARIOS = os.path.join(BASE_DIR, "..", "data", "usuarios.json")


# Función para cargar usuarios
def cargar_usuarios():
    if os.path.exists(ARCHIVO_USUARIOS):
        with open(ARCHIVO_USUARIOS, "r") as file:
            return json.load(file)
    return {"empleados": {}, "administradores": {}}

# Función para guardar usuarios en el JSON
def guardar_usuarios(usuarios):
    """
    Guarda la lista de empleados en el archivo JSON.
    """
    with open(ARCHIVO_USUARIOS, "w") as file:
        json.dump(usuarios, file, indent=4)

# Función para verificar si hay una sesión activa, si no, redirige al login.
def verificar_sesion(request: Request):
    """Verifica si hay una sesión activa. Si no, redirige a login."""
    session = request.cookies.get("session")
    if not session or session == "deleted":  # Si la cookie fue eliminada
        return RedirectResponse(url="/login", status_code=303)

    return session  # Retorna el usuario autenticado si hay sesión activa

# Ruta para mostrar el perfil del empleado y la pagina donde puede marcar asistencia.
@router.get("/empleado/{codigo}")
async def perfil_empleado(request: Request, codigo: str, session=Depends(verificar_sesion)):
    
    USUARIOS = cargar_usuarios()

    if codigo in USUARIOS["empleados"]:
        codigo = USUARIOS["empleados"][codigo].get("codigo")  # Obtener el código real
                
    empleado = next((nombre for nombre, data in USUARIOS["empleados"].items() if data.get("codigo") == codigo), None)
    
    if not empleado:
        return templates.TemplateResponse("error.html", {"request": request, "mensaje": "Empleado no encontrado."})

    return templates.TemplateResponse("empleado.html", {"request": request, "empleado": empleado, "codigo": codigo})