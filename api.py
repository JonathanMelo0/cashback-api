import os
import psycopg2
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Configuração de CORS para permitir acesso da Vercel
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Puxa o link do banco das variáveis de ambiente do Render
DATABASE_URL = os.getenv("DATABASE_URL")

def get_db_connection():
    return psycopg2.connect(DATABASE_URL)

@app.get("/calcular")
def calcular(valor: float, tipo: str, request: Request, cupom: float = 0):
    # Identifica o IP do usuário para o histórico privado
    ip_cliente = request.headers.get("x-forwarded-for", "").split(",")[0] or request.client.host
    
    conn = None
    try:
        # 1. Aplicar desconto do cupom primeiro
        valor_com_desconto = valor * (1 - (cupom / 100))
        
        # 2. Regra: 5% base. Se a compra for > 500, a taxa base dobra (10%)
        taxa_base = 0.10 if valor_com_desconto > 500 else 0.05
        cashback_inicial = valor_com_desconto * taxa_base
        
        # 3. Regra VIP: Ganha 10% de bônus SOBRE o cashback calculado
        if tipo.lower() == "vip":
            cashback_inicial *= 1.10
            
        cashback_final = round(cashback_inicial, 2)

        # 4. Salva no Banco com o IP
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
        print(f"Erro no servidor: {e}")
        return {"error": "Falha ao processar dados"}, 500
    finally:
        if conn:
            conn.close() # GARANTE que a conexão feche e o banco não fique lento

@app.get("/historico")
def historico(request: Request):
    ip_cliente = request.headers.get("x-forwarded-for", "").split(",")[0] or request.client.host
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        # Filtra para mostrar apenas o que esse IP calculou
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
            conn.close()