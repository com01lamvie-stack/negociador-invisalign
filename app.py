from fastapi import FastAPI
from pydantic import BaseModel
from scipy.optimize import minimize
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Permitir acesso do navegador (frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

VALOR_LIGN = 7150.0
VALOR_LAMVIE = 9500.0

class Requisicao(BaseModel):
    meta_mensal: float
    entrada_lign: float = 0
    entrada_lamvie: float = 0
    parcelas_lign: int = 14
    parcelas_lamvie: int = 14
    max_desconto_pct_lign: float = 30
    max_desconto_pct_lamvie: float = 30

def calcula_mensal_total(dl, dm, entrada_lign, entrada_lamvie, parcelas_lign, parcelas_lamvie):
    valor_lign = VALOR_LIGN * (1 - dl / 100.0)
    valor_lamvie = VALOR_LAMVIE * (1 - dm / 100.0)
    restante_lign = max(0, valor_lign - entrada_lign)
    restante_lamvie = max(0, valor_lamvie - entrada_lamvie)
    parcela_lign = restante_lign / parcelas_lign
    parcela_lamvie = restante_lamvie / parcelas_lamvie
    return parcela_lign + parcela_lamvie

def otimizar(meta_mensal, entrada_lign, entrada_lamvie, parcelas_lign, parcelas_lamvie, max_l, max_m):
    def objetivo(x):
        dl, dm = x
        mensal = calcula_mensal_total(dl, dm, entrada_lign, entrada_lamvie, parcelas_lign, parcelas_lamvie)
        return abs(mensal - meta_mensal) + 0.5 * (dl + dm)

    limites = [(0, max_l), (0, max_m)]
    inicial = [5.0, 5.0]
    resultado = minimize(objetivo, inicial, bounds=limites, method='TNC')

    dl, dm = resultado.x
    mensal = calcula_mensal_total(dl, dm, entrada_lign, entrada_lamvie, parcelas_lign, parcelas_lamvie)
    return {
        "desconto_lign": round(dl, 2),
        "desconto_lamvie": round(dm, 2),
        "mensal_total": round(mensal, 2),
        "diferenca_meta": round(abs(mensal - meta_mensal), 2),
        "sucesso": resultado.success
    }

@app.post("/otimizar")
def otimizar_endpoint(req: Requisicao):
    return otimizar(
        req.meta_mensal,
        req.entrada_lign,
        req.entrada_lamvie,
        req.parcelas_lign,
        req.parcelas_lamvie,
        req.max_desconto_pct_lign,
        req.max_desconto_pct_lamvie,
    )

@app.get("/")
def home():
    return {"mensagem": "API Negociador Invisalign ativa!"}
