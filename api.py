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
    # Identifica o IP para o histórico privado
    ip_cliente = request.headers.get("x-forwarded-for") or request.client.host

    # 1. Aplicar o cupom sobre o valor original
    # Se cupom for 0, valor_pago será igual ao valor original.
    valor_pago = valor * (1 - (cupom / 100))
    
    # 2. Definir a TAXA BASE (usando decimais corretos!)
    taxa_base = 0.05  # 5%
    
    # REGRA: Se a compra (já com desconto) for acima de 500, a taxa dobra (10%)
    if valor_pago > 500:
        taxa_base = 0.10  # 10%
        
    # 3. Cálculo do Cashback Inicial
    cashback = valor_pago * taxa_base
    
    # 4. REGRA VIP: 10% a mais SOBRE o valor do cashback (bônus de 1.1x)
    if tipo.lower() == "vip":
        cashback = cashback * 1.10
        
    # 5. ARREDONDAMENTO (Crucial para não virar um número gigante)
    cashback_final = round(cashback, 2)

    # Salva no Banco
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO consultas (tipo, valor, cashback, ip) VALUES (%s, %s, %s, %s)",
            (tipo, round(valor_pago, 2), cashback_final, ip_cliente)
        )
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"❌ Erro ao salvar: {e}")
    
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