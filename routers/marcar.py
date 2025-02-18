import os
import csv
from datetime import datetime, time
from fastapi import APIRouter, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="templates")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ARCHIVO_REGISTRO = os.path.join(BASE_DIR, "..", "registro_horas.csv")

# Función para registrar entrada/salida con validaciones
def registrar_evento(codigo: str, tipo: str):
    """
    Registra la llegada o salida de un empleado con validaciones:
    - Solo una entrada/salida por día.
    - Restricciones horarias.
    """
    fecha_hora = datetime.now()
    fecha = fecha_hora.strftime("%Y-%m-%d")
    hora = fecha_hora.strftime("%H:%M:%S")
    hora_actual = fecha_hora.time()

    limite_llegada_min = time(6, 30)
    limite_llegada_max = time(12, 0)
    limite_salida_min = time(12, 0)
    limite_salida_max = time(19, 0)

# Lee registros existentes.
    registros = []
    if os.path.exists(ARCHIVO_REGISTRO):
        with open(ARCHIVO_REGISTRO, mode="r") as file:
            registros = list(csv.reader(file))

# Verifica si ya registro entrada/salida hoy.    
#    for row in registros:
#        if row[0] == codigo and row[1] == fecha and row[3] == tipo:
#            return f"restriccion_{tipo}_duplicada.html", f"Error: Ya registraste una {tipo} hoy."

# Verifica restricciones de horario.

    if tipo == "entrada" and not (limite_llegada_min <= hora_actual <= limite_llegada_max):
            return "restriccion_entrada.html", "Error: El registro de entrada solo está permitido entre 6:30 AM y 12:00 PM."

    if tipo == "salida" and not (limite_salida_min <= hora_actual <= limite_salida_max):
            return "restriccion_salida.html", "Error: El registro de salida solo está permitido entre 12:00 PM y 7:00 PM."


# Escribe registro en el csv.
    with open(ARCHIVO_REGISTRO, mode="a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([codigo, fecha, hora, tipo])

    return "Registro exitoso."

@router.post("/marcar/{codigo}")
async def marcar_hora(request: Request, codigo: str, tipo: str = Form(...)):
    """
    Procesa la marcación de asistencia.
    """

    mensaje = registrar_evento(codigo, tipo) # Procesa el registro con validaciones.

     # Si el mensaje es un error relacionado con restricciones de salida, mostrar página con botón de regreso

    template, mensaje = registrar_evento(codigo, tipo)

    if template:
        return templates.TemplateResponse(template, {"request": request, "mensaje": mensaje, "codigo": codigo})

    return RedirectResponse(url=f"/empleado/{codigo}?mensaje={mensaje}", status_code=303)
