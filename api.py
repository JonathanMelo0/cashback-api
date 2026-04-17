import os
import psycopg2
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Permite que o site na Vercel acesse a API no Render
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pega o link do banco das configurações do Render
DATABASE_URL = os.getenv("DATABASE_URL")

def get_db_connection():
    return psycopg2.connect(DATABASE_URL)

@app.get("/calcular")
def calcular(valor: float, tipo: str, cupom: float = 0):
    # Lógica de Cashback
    porcentagem = 0.10 if tipo.lower() == "vip" else 0.05
    cashback = (valor * porcentagem) + (valor * (cupom / 100))
    
    # Salva no Banco (usando os novos nomes de colunas)
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO consultas (tipo, valor, cashback) VALUES (%s, %s, %s)",
        (tipo, valor, cashback)
    )
    conn.commit()
    cur.close()
    conn.close()
    
    return {"cashback": round(cashback, 2)}

@app.get("/historico")
def historico():
    conn = get_db_connection()
    cur = conn.cursor()
    # Busca os dados ordenando pelo mais recente
    cur.execute("SELECT tipo, valor, cashback FROM consultas ORDER BY data_consulta DESC LIMIT 10")
    dados = cur.fetchall()
    cur.close()
    conn.close()
    
    # Formata para o JavaScript entender
    return [{"tipo": d[0], "valor": d[1], "cashback": d[2]} for d in dados]