from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import psycopg2
import os

app = FastAPI(title="Sistema de Cashback")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# URL do banco (vem do Render)
DATABASE_URL = os.getenv("DATABASE_URL")


def calcular_cashback(valor, tipo, cupom):
    valor_final = valor * (1 - cupom / 100)

    cashback = valor_final * 0.05

    if valor_final > 500:
        cashback *= 2

    if tipo.lower() == "vip":
        cashback *= 1.10

    return round(cashback, 2)


@app.get("/calcular")
def calcular(request: Request, valor: float, tipo: str, cupom: float = 0):
    cashback = calcular_cashback(valor, tipo, cupom)
    ip = request.client.host

    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()

        cur.execute(
            "INSERT INTO consultas (ip, tipo_cliente, valor, cashback) VALUES (%s, %s, %s, %s)",
            (ip, tipo, valor, cashback)
        )

        conn.commit()
        cur.close()
        conn.close()

    except Exception as e:
        print("Erro ao salvar no banco:", e)

    return {"cashback": cashback}


@app.get("/historico")
def historico(request: Request):
    ip = request.client.host

    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()

        cur.execute(
            "SELECT tipo_cliente, valor, cashback FROM consultas WHERE ip = %s ORDER BY id DESC",
            (ip,)
        )

        dados = cur.fetchall()

        cur.close()
        conn.close()

        # 🔥 retorno estruturado (corrige seu JS)
        return [
            {"tipo": d[0], "valor": d[1], "cashback": d[2]}
            for d in dados
        ]

    except Exception as e:
        print("Erro ao buscar histórico:", e)
        return []