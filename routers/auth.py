import json
import random
import os
from fastapi import APIRouter, Request, Form, Depends, Response
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse


router = APIRouter()
templates = Jinja2Templates(directory="templates")

# Obtener la ruta absoluta del archivo usuarios.json
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Directorio actual de routes/
ARCHIVO_USUARIOS = os.path.join(BASE_DIR, "..", "data/usuarios.json")  # Ubicación en la raíz del proyecto

# Funcion para Cargar usuarios desde el JSON
def cargar_usuarios():
    if os.path.exists(ARCHIVO_USUARIOS):
        with open(ARCHIVO_USUARIOS, "r") as file:
            return json.load(file)
    return {"empleados": {}, "administradores": {}}

# Cargar usuarios antes de la autenticación
USUARIOS = cargar_usuarios()    


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """
    Muestra la página de inicio de sesión.
    - Si el usuario ya tiene sesión activa, lo redirige a su perfil.
    """
    if request.cookies.get("session"):
        return RedirectResponse(url="/empleado/{codigo}", status_code=303)
    
    return templates.TemplateResponse("login.html", {"request": request})


@router.post("/login")
async def login(request: Request, response: Response, username: str = Form(...), password: str = Form(...)):

    USUARIOS = cargar_usuarios()

     # Validar credenciales de empleados
    if username in USUARIOS["empleados"] and USUARIOS["empleados"][username]["password"] == password:
        codigo_empleado = USUARIOS["empleados"][username].get("codigo")  # Obtener código, si existe
        
        if not codigo_empleado:  # Si no hay código, evitar error
            return templates.TemplateResponse("login.html", {"request": request, "error": "Error en el sistema, falta código del usuario."})

        response = RedirectResponse(url=f"/empleado/{codigo_empleado}", status_code=303)
        response.set_cookie(key="session", value=username, httponly=True)
        return response
    
      # Validar credenciales de administradores
    if username in USUARIOS["administradores"] and USUARIOS["administradores"][username]["password"] == password:
        response = RedirectResponse(url="/admin", status_code=303)
        response.set_cookie(key="session", value="admin", httponly=True)
        return response

    # Si las credenciales son incorrectas, mostrar error en la página de login
    return templates.TemplateResponse("login.html", {"request": request, "error": "Usuario o contraseña incorrectos."})


@router.get("/logout")
def logout(response: Response):
    """
    Cierra la sesión eliminando la cookie de sesión y redirige a login.
    - Usa `GET` para permitir la redirección desde un enlace.
    - Elimina la cookie `session` para invalidar la sesión.
    - Deshabilita el caché para evitar que el usuario pueda volver atrás y ver su sesión.
    """
    response = RedirectResponse(url="/login", status_code=303)

    # ❌ Elimina la cookie de sesión correctamente
    response.delete_cookie("session", path="/", domain=None)

    # Evita que el navegador guarde la sesión en caché
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"


    return response