import json
import os
import random
from fastapi import APIRouter, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from routers.empleados import cargar_usuarios, guardar_usuarios

router = APIRouter()
templates = Jinja2Templates(directory="templates")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ARCHIVO_USUARIOS = os.path.join(BASE_DIR, "..", "usuarios.json")
ARCHIVO_TRABAJOS = os.path.join(BASE_DIR, "..", "trabajos.json")



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
    empleados = USUARIOS.get("empleados", {})  # ✅ Ahora empleados es un diccionario
    trabajos = cargar_trabajos().get("trabajos", [])

    empleados_lista = [{"usuario": usuario, "codigo": data.get("codigo", "Sin código")} for usuario, data in empleados.items()]


    return templates.TemplateResponse("admin.html", {"request": request, "empleados": empleados_lista, "trabajos":trabajos})

@router.post("/admin/agregar_trabajo")
async def agregar_trabajo(nombre_trabajo: str = Form(...), direccion_trabajo: str = Form(...)):
    """
    Agrega un nuevo trabajo con nombre y direccion.
    """
    trabajos = cargar_trabajos().get("trabajos",[])
    trabajos.append({"nombre": nombre_trabajo, "direccion": direccion_trabajo})
    guardar_trabajos(trabajos)
    return RedirectResponse(url="/admin", status_code=303)

@router.post("/admin/eliminar_trabajo")
async def eliminar_trabajo(nombre_trabajo: str = Form(...)):
    """
    Elimina un trabajo de la lista.
    """
    trabajos = cargar_trabajos().get("trabajos", [])
    trabajos_filtrados = [t for t in trabajos if t["nombre"] != nombre_trabajo]  # ✅ Filtrar correctamente
    guardar_trabajos(trabajos_filtrados)
    return RedirectResponse(url="/admin", status_code=303)

@router.post("/admin/agregar_empleado")
async def agregar_empleado(usuario: str = Form(...), password: str = Form(...)):
    """
    Agrega un nuevo empleado al sistema con usuario y contraseña.
    """
    USUARIOS = cargar_usuarios()

    # Verificar si el usuario ya existe
    if usuario in USUARIOS.get("empleados", {}):
        return RedirectResponse(url="/admin?error=Usuario ya existe", status_code=303)

    # Generar un código único de 6 dígitos
    codigo_generado = str(random.randint(100000, 999999))

    # Asegurar que el código sea único
    codigos_existentes = {data["codigo"] for data in USUARIOS["empleados"].values() if "codigo" in data}
    while codigo_generado in codigos_existentes:
        codigo_generado = str(random.randint(100000, 999999))

    # Agregar nuevo empleado con codigo
    USUARIOS["empleados"][usuario] = {"password": password, "codigo": codigo_generado}
    guardar_usuarios(USUARIOS)
    return RedirectResponse(url="/admin", status_code=303)

@router.post("/admin/eliminar_empleado")
async def eliminar_empleado(usuario: str = Form(...)):
    """
    Elimina un empleado del sistema.
    """
    USUARIOS = cargar_usuarios()
    
    if usuario in USUARIOS.get("empleados", {}):
        del USUARIOS["empleados"][usuario]
        guardar_usuarios(USUARIOS)
    
    return RedirectResponse(url="/admin", status_code=303)