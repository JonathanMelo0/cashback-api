from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import psycopg2
import os

app = FastAPI(title="Sistema de Cashback")

# 🔥 CORS (necessário pro frontend funcionar)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🔗 conexão com banco do Render
DATABASE_URL = os.getenv(postgresql://cashback_user:egRoWm40ANB2ACve3IkMR9nOB2NDxPko@dpg-d7glo1nlk1mc7398buv0-a.ohio-postgres.render.com/cashback_ndxs)


# 🧠 função de cálculo
def calcular_cashback(valor, tipo, cupom):
    valor_final = valor * (1 - cupom / 100)

    cashback = valor_final * 0.05

    if valor_final > 500:
        cashback *= 2

    if tipo.lower() == "vip":
        cashback *= 1.10

    return round(cashback, 2)


# 💰 endpoint de cálculo + salvar no banco
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


# 📊 endpoint de histórico por IP
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

        return dados

    except Exception as e:
        print("Erro ao buscar histórico:", e)
        return []


# ▶️ rodar local (opcional)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)