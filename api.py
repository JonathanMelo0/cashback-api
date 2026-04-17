from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import psycopg2
import psycopg2.extras
import os

app = FastAPI(title="Sistema de Cashback Fintech")

# 1. Configuração de CORS - Permite que seu index.html fale com a API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. URL do Banco de Dados (Use a EXTERNAL URL do Render aqui)
# Para rodar local, substitua o os.getenv pela string da URL entre aspas
DATABASE_URL = "postgresql://cashback_user:egRoWm40ANB2ACve3IkMR9nOB2NDxPko@dpg-d7glo1nlk1mc7398buv0-a.ohio-postgres.render.com/cashback_ndxs"

# Função auxiliar para o cálculo (Regras do PO, Diretor e VIP)
def calcular_valor_cashback(valor, tipo, cupom):
    # Regra 1: Valor após descontos
    valor_final = valor * (1 - cupom / 100)

    # Regra 2: Cashback base de 5%
    cashback = valor_final * 0.05

    # Regra 3: Se compra > 500, dobra o cashback
    if valor_final > 500:
        cashback *= 2

    # Regra 4: VIP ganha +10% sobre o cashback calculado
    if tipo.lower() == "vip":
        cashback *= 1.10

    return round(cashback, 2)

@app.get("/")
def home():
    return {"status": "API Online", "projeto": "Sistema de Cashback Fintech"}

@app.get("/calcular")
def calcular(request: Request, valor: float, tipo: str, cupom: float = 0):
    cashback = calcular_valor_cashback(valor, tipo, cupom)
    ip = request.client.host

    try:
        # Conecta ao Postgres
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()

        # INSERT usando os nomes exatos da sua tabela historico_cashback
        cur.execute(
            "INSERT INTO historico_cashback (ip_usuario, tipo_cliente, valor_compra, valor_cashback) VALUES (%s, %s, %s, %s)",
            (ip, tipo.upper(), valor, cashback)
        )

        conn.commit()
        cur.close()
        conn.close()

    except Exception as e:
        print(f"❌ Erro ao salvar no banco: {e}")

    return {
        "cashback": cashback,
        "tipo_cliente": tipo,
        "valor_original": valor,
        "cupom_aplicado": cupom
    }

@app.get("/historico")
def historico(request: Request):
    ip = request.client.host

    try:
        conn = psycopg2.connect(DATABASE_URL)
        # Usamos DictCursor para o retorno vir com os nomes das chaves para o JS
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        # SELECT filtrando pelo IP do usuário (Requisito 5)
        cur.execute(
            "SELECT tipo_cliente, valor_compra as valor, valor_cashback as cashback FROM historico_cashback WHERE ip_usuario = %s ORDER BY id DESC",
            (ip,)
        )

        dados = cur.fetchall()
        cur.close()
        conn.close()

        return dados

    except Exception as e:
        print(f"❌ Erro ao buscar histórico: {e}")
        return []

if __name__ == "__main__":
    import uvicorn
    # Roda a API na porta 8000
    uvicorn.run(app, host="127.0.0.1", port=8000)