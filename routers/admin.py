import json
import os
from fastapi import APIRouter, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse

router = APIRouter()
templates = Jinja2Templates(directory="templates")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ARCHIVO_USUARIOS = os.path.join(BASE_DIR, "..", "usuarios.json")
ARCHIVO_TRABAJOS = os.path.join(BASE_DIR, "..", "trabajos.json")


def cargar_usuarios():
    
    # Carga la lista de empleados desde el archivo JSON.
    if os.path.exists(ARCHIVO_USUARIOS):
        with open(ARCHIVO_USUARIOS, "r") as file:
            return json.load(file)
    return {"empleados": {}, "administradores": {}}

def cargar_trabajos():
    """Carga la lista de trabajos desde el archivo JSON."""
    if os.path.exists(ARCHIVO_TRABAJOS):
        with open(ARCHIVO_TRABAJOS, "r") as file:
            return json.load(file)
    return {"trabajos": []}

def guardar_trabajos(trabajos):
    """Guarda la lista de trabajos en el archivo JSON."""
    with open(ARCHIVO_TRABAJOS, "w") as file:
        json.dump({"trabajos": trabajos}, file, indent=4)


@router.get("/admin", response_class=HTMLResponse)
async def admin_panel(request: Request):

    """
    Muestra la página de administración con la lista de empleados y trabajos.
    Cada empleado tendrá un botón para ver su historial de asistencia.
    """
    USUARIOS = cargar_usuarios()
    trabajos = cargar_trabajos()["trabajos"]


    # Genera una lista de empleados con su nombre y código
    empleados = [{"nombre": nombre, "codigo": data["codigo"]} for nombre, data in USUARIOS["empleados"].items()]

    return templates.TemplateResponse("admin.html", {"request": request, "empleados": empleados, "trabajos":trabajos})

@router.post("/admin/agregar_trabajo")
async def agregar_trabajo(nombre_trabajo: str = Form(...), direccion_trabajo: str = Form(...)):
    """
    Agrega un nuevo trabajo con nombre y direccion.
    """
    trabajos = cargar_trabajos()["trabajos"]
    trabajos.append({"nombre": nombre_trabajo, "direccion": direccion_trabajo})
    guardar_trabajos(trabajos)
    return RedirectResponse(url="/admin", status_code=303)

@router.post("/admin/eliminar_trabajo")
async def eliminar_trabajo(nombre_trabajo: str = Form(...)):
    """
    Elimina un trabajo de la lista.
    """
    trabajos_data = cargar_trabajos()
    trabajos = trabajos_data["trabajos"]


    # Verificamos si la lista tiene la estructura correcta (diccionarios con "nombre" y "direccion")
    if isinstance(trabajos, list) and all(isinstance(t, dict) and "nombre" in t for t in trabajos):
        trabajos_filtrados = [t for t in trabajos if t["nombre"] != nombre_trabajo]  # Filtra correctamente
    else:
        # Si los trabajos están en formato incorrecto, los convertimos en una lista de diccionarios
        trabajos_filtrados = [{"nombre": t, "direccion": ""} for t in trabajos if t != nombre_trabajo]

    guardar_trabajos(trabajos_filtrados)
    return RedirectResponse(url="/admin", status_code=303)