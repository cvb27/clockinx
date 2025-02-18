import os
import csv
from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from datetime import datetime, timedelta

router = APIRouter()
templates = Jinja2Templates(directory="templates")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ARCHIVO_REGISTRO = os.path.join(BASE_DIR, "..", "registro_horas.csv")

@router.get("/historial/{codigo}", response_class=HTMLResponse)
async def ver_historial(request: Request, codigo: str):
    """
    Muestra el historial de asistencia de un empleado.
    - Si es un administrador, regresa a `/admin`.
    - Si es un empleado, regresa a su perfil `/empleado/{codigo}`.
    """
    registros = []
    if os.path.exists(ARCHIVO_REGISTRO):
        with open(ARCHIVO_REGISTRO, mode="r") as file:
            registros = list(csv.reader(file))

    registros_empleado = [row for row in registros if row[0] == codigo]

     # Verificar si el usuario es un administrador
    if request.cookies.get("session") == "admin":
        home_url = "/admin"
    else:
        home_url = f"/empleado/{codigo}"

    return templates.TemplateResponse("historial.html", {
        "request": request,
        "codigo": codigo,
        "registros": registros_empleado,
        "home_url": home_url
    })
