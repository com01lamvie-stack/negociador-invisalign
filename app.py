from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

app = FastAPI()

# Montar a pasta de arquivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def read_root():
    return FileResponse("static/index.html")

@app.get("/status")
def status():
    return {"mensagem": "API Negociador Invisalign ativa!"}

@app.post("/otimizar")
def otimizar():
    return {"mensagem": "Aqui futuramente entra o cálculo de negociação"}
