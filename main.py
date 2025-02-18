from fastapi import FastAPI
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from datetime import datetime
from routers import index, auth, empleados, admin, marcar, historial
import csv
import os

app = FastAPI()

# Sirve archivos estaticos (css, imagenes, etc.)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Configurar la carpeta de las plantillas.
templates = Jinja2Templates(directory="templates")

app.include_router(index.router)
app.include_router(auth.router)
app.include_router(empleados.router)
app.include_router(admin.router)
app.include_router(marcar.router)
app.include_router(historial.router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
