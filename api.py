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
    # 1. Aplicar o desconto do cupom primeiro
    valor_com_desconto = valor * (1 - cupom / 100)
    
    # 2. Definir a taxa base (5%)
    taxa_base = 0.05
    
    # 3. Regra: Se a compra (pós-desconto) for acima de 500, o cash de 5% dobra
    if valor_com_desconto > 500:
        taxa_base = 0.10  # O dobro de 5%
        
    # 4. Calcular o cashback inicial
    cashback_calculado = valor_com_desconto * taxa_base
    
    # 5. Regra VIP: Se for VIP, ganha 10% a mais SOBRE o cashback calculado
    if tipo.lower() == "vip":
        # Multiplicar por 1.10 adiciona 10% ao valor existente
        cashback_calculado = cashback_calculado * 1.10
        
    # Arredondar para 2 casas decimais
    cashback_final = round(cashback_calculado, 2)
    
    # Salva no Banco (usando a tabela 'consultas' que criamos)
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO consultas (tipo, valor, cashback) VALUES (%s, %s, %s)",
        (tipo, valor_com_desconto, cashback_final)
    )
    conn.commit()
    cur.close()
    conn.close()
    
    return {"cashback": cashback_final}

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