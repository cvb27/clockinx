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
             reader = csv.reader(file)
             for row in reader:
                if row and row[0] == codigo: # ✅ Verificar que la fila no esté vacía
                    fecha = row[1]
                    hora = row[2]
                    tipo = row[3] if len(row) > 3 else ""
                    
                    # Convertir fecha a formato "Day" y "Date"
                    fecha_obj = datetime.strptime(fecha, "%Y-%m-%d")
                    day = fecha_obj.strftime("%A")  # Nombre del día en inglés
                    date = fecha_obj.strftime("%Y-%m-%d")  # Fecha en formato YYYY-MM-DD

                    # Buscar si ya hay un registro en la misma fecha
                    existe = next((r for r in registros if r["date"] == date), None)

                    if existe:
                        if tipo == "entrada":
                            existe["in"] = hora
                        elif tipo == "salida":
                            existe["out"] = hora
                    else:
                        registros.append({
                            "day": day,
                            "date": date,
                            "in": hora if tipo == "entrada" else "",
                            "out": hora if tipo == "salida" else ""})

 # ✅ Asegurar que `registros` no esté vacío antes de renderizar
    if not registros:
        registros.append({"day": "No records", "date": "No records", "in": "No records", "out": "No records"})



    return templates.TemplateResponse("historial.html", {
        "request": request,
        "codigo": codigo,
        "registros": registros
    })
