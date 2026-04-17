import os
import psycopg2
from fastapi import FastAPI, Request # Adicionamos o Request aqui
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DATABASE_URL = os.getenv("DATABASE_URL")

def get_db_connection():
    return psycopg2.connect(DATABASE_URL)

@app.get("/calcular")
def calcular(valor: float, tipo: str, request: Request, cupom: float = 0):
    # Identifica o IP do usuário (no Render, usamos o header 'x-forwarded-for')
    ip_cliente = request.headers.get("x-forwarded-for") or request.client.host

    # Sua lógica de cálculo (que já está certa)
    valor_com_desconto = valor * (1 - cupom / 100)
    taxa_base = 0.10 if valor_com_desconto > 500 else 0.05
    cashback_calculado = valor_com_desconto * taxa_base
    if tipo.lower() == "vip":
        cashback_calculado *= 1.10
    
    cashback_final = round(cashback_calculado, 2)

    # SALVA COM O IP
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO consultas (tipo, valor, cashback, ip) VALUES (%s, %s, %s, %s)",
        (tipo, valor_com_desconto, cashback_final, ip_cliente)
    )
    conn.commit()
    cur.close()
    conn.close()
    
    return {"cashback": cashback_final}

@app.get("/historico")
def historico(request: Request):
    # Identifica quem está pedindo o histórico
    ip_cliente = request.headers.get("x-forwarded-for") or request.client.host

    conn = get_db_connection()
    cur = conn.cursor()
    
    # BUSCA APENAS OS DADOS DESSE IP ESPECÍFICO
    cur.execute(
        "SELECT tipo, valor, cashback FROM consultas WHERE ip = %s ORDER BY data_consulta DESC LIMIT 10",
        (ip_cliente,)
    )
    
    dados = cur.fetchall()
    cur.close()
    conn.close()
    
    return [{"tipo": d[0], "valor": d[1], "cashback": d[2]} for d in dados]