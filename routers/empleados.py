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
ARCHIVO_USUARIOS = os.path.join(BASE_DIR, "..", "usuarios.json")


# Función para cargar usuarios
def cargar_usuarios():
    if os.path.exists(ARCHIVO_USUARIOS):
        with open(ARCHIVO_USUARIOS, "r") as file:
            return json.load(file)
    return {"empleados": {}, "administradores": {}}

def verificar_sesion(request: Request):
    """Verifica si hay una sesión activa. Si no, redirige a login."""
    if not request.cookies.get("session"):
        return RedirectResponse(url="/login", status_code=303)

@router.get("/empleado/{codigo}")
async def perfil_empleado(request: Request, codigo: str, session=Depends(verificar_sesion)):
    USUARIOS = cargar_usuarios()
    empleado = next((nombre for nombre, data in USUARIOS["empleados"].items() if data["codigo"] == codigo), None)
    if not empleado:
        return templates.TemplateResponse("error.html", {"request": request, "mensaje": "Empleado no encontrado."})
    response = templates.TemplateResponse("empleado.html", {"request": request, "empleado": empleado, "codigo": codigo})
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    return response