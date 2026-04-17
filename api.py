import os
import psycopg2
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# FORMA CORRETA: O link deve estar configurado no painel do Render como DATABASE_URL
DATABASE_URL = os.getenv("DATABASE_URL")

def get_db_connection():
    return psycopg2.connect(DATABASE_URL)

@app.get("/calcular")
def calcular(valor: float, tipo: str, request: Request, cupom: float = 0):
    # 1. Identifica o IP real do usuário (essencial para o histórico privado)
    ip_cliente = request.headers.get("x-forwarded-for") or request.client.host
    
    conn = None
    try:
        # 2. Lógica de Cálculo
        valor_com_desconto = valor * (1 - (cupom / 100))
        
        # Regra: 5% base. Se for > 500, dobra para 10%
        taxa = 0.10 if valor_com_desconto > 500 else 0.05
        cashback = valor_com_desconto * taxa
        
        # Regra VIP: +10% em cima do cashback
        if tipo.lower() == "vip":
            cashback *= 1.10
            
        cashback_final = round(cashback, 2)

        # 3. Salva no Banco
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO consultas (tipo, valor, cashback, ip) VALUES (%s, %s, %s, %s)",
            (tipo, round(valor_com_desconto, 2), cashback_final, ip_cliente)
        )
        conn.commit()
        cur.close()
        return {"cashback": cashback_final}
        
    except Exception as e:
        print(f"Erro ao calcular/salvar: {e}")
        return {"error": "Erro interno no servidor"}, 500
    finally:
        if conn:
            conn.close() # Libera a conexão para o banco não ficar lento

@app.get("/historico")
def historico(request: Request):
    ip_cliente = request.headers.get("x-forwarded-for") or request.client.host
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        # Filtra apenas pelo IP de quem está acessando
        cur.execute(
            "SELECT tipo, valor, cashback FROM consultas WHERE ip = %s ORDER BY data_consulta DESC LIMIT 10",
            (ip_cliente,)
        )
        dados = cur.fetchall()
        cur.close()
        return [{"tipo": d[0], "valor": d[1], "cashback": d[2]} for d in dados]
    except Exception as e:
        print(f"Erro ao buscar histórico: {e}")
        return []
    finally:
        if conn:
            conn.close() # Evita o travamento do banco