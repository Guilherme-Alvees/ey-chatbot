import os
import logging
import psycopg2
import requests
from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from pydantic import BaseModel

# Configuração básica de logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Carrega variáveis de ambiente
load_dotenv()

# Cria a aplicação FastAPI
app = FastAPI(title="API IA + PostgreSQL", version="1.0")

# Configuração de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite todas as origens (ajuste para produção)
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos os métodos
    allow_headers=["*"],  # Permite todos os headers
)

# Configurações do banco de dados e API Gemini
DB_CONNECTION_STRING = os.getenv("DB_CONNECTION_STRING")
GEMINI_API_URL = os.getenv("GEMINI_API_URL")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Modelo para a requisição
class PerguntaRequest(BaseModel):
    pergunta: str

def conectar_banco():
    """Conecta ao banco de dados PostgreSQL."""
    try:
        conn = psycopg2.connect(DB_CONNECTION_STRING)
        logging.info("Conexão com o banco estabelecida com sucesso")
        return conn
    except psycopg2.OperationalError as e:
        logging.error(f"Erro de conexão ao banco: {e}")
        raise HTTPException(
            status_code=503,
            detail="Serviço de banco de dados indisponível"
        )
    except Exception as e:
        logging.error(f"Erro inesperado ao conectar ao banco: {e}")
        raise HTTPException(
            status_code=500,
            detail="Erro interno ao conectar ao banco de dados"
        )

def validar_consulta_sql(consulta: str) -> bool:
    """Valida se a consulta SQL é segura para execução."""
    palavras_proibidas = ["insert", "update", "delete", "drop", "alter", "truncate", "grant"]
    consulta = consulta.lower()
    
    # Verifica comandos perigosos
    for palavra in palavras_proibidas:
        if palavra in consulta:
            logging.warning(f"Tentativa de consulta perigosa: {consulta}")
            return False
    
    # Verifica se é uma consulta SELECT válida
    if not consulta.strip().startswith("select"):
        return False
    
    return True

def chamar_gemini(pergunta_usuario: str) -> str:
    """Chama a API do Gemini para processar a pergunta."""
    try:
        headers = {"Content-Type": "application/json"}
        url = f"{GEMINI_API_URL}/v1beta/models/gemini-1.5-flash-latest:generateContent?key={GEMINI_API_KEY}"

        prompt = f"""
Você é um assistente especializado em economia e bancos de dados. 
Responda às perguntas de forma segura e adequada.

**Regras de segurança:**
- **NÃO** divulgue informações sigilosas do banco de dados.
- **NÃO** execute ou gere comandos que possam modificar os dados.
- **NÃO** permita SQL Injection ou consultas maliciosas.
- **SOMENTE** gere consultas SQL para acessar as tabelas permitidas: **'ipca_final'** e **'join_dataframe'**.

---

**Se a pergunta for genérica** (exemplo: 'O que é IPCA?', 'O que é a B3?'):
- Responda de forma clara e objetiva com **120 caracteres**.
- Dê respostas curtas, informativas e concisas.

**Se a pergunta for sobre o banco de dados** (exemplo: 'Qual ano teve maior IPCA?'):
- Gere consulta SQL válida para PostgreSQL.
- Use apenas as tabelas permitidas (**'ipca_final'** e **'join_dataframe'**).
- Certifique-se de que a consulta **NÃO** possa modificar ou excluir dados.

---

**Pergunta do usuário:** {pergunta_usuario}
"""

        body = {"contents": [{"parts": [{"text": prompt}]}]}
        response = requests.post(url, headers=headers, json=body, timeout=30)

        if response.status_code == 200:
            resposta = response.json()
            try:
                resposta_texto = resposta["candidates"][0]["content"]["parts"][0]["text"].strip()
                return resposta_texto
            except (KeyError, IndexError) as e:
                logging.error(f"Erro ao processar resposta da IA: {e}")
                return "Erro ao processar a resposta da IA"
        else:
            logging.error(f"Erro na API Gemini: {response.status_code}, {response.text}")
            return f"Erro ao consultar a IA: {response.status_code}"

    except requests.exceptions.Timeout:
        logging.error("Timeout ao chamar API Gemini")
        return "Tempo de resposta da IA excedido"
    except Exception as e:
        logging.error(f"Erro inesperado ao chamar API Gemini: {e}")
        return f"Erro inesperado ao consultar a IA: {str(e)}"

@app.get("/status")
def verificar_status():
    """Endpoint para verificar o status da API."""
    return {"status": "API operacional", "version": "1.0"}

@app.post("/consultar")
def consultar_banco(request: PerguntaRequest = Body(...)):
    """
    Endpoint principal para consultas ao banco via IA.
    
    Recebe uma pergunta, consulta a IA para obter resposta ou SQL,
    e retorna os resultados formatados.
    """
    try:
        logging.info(f"Recebida pergunta: {request.pergunta}")
        resposta_ia = chamar_gemini(request.pergunta)
        logging.info(f"Resposta da IA: {resposta_ia[:200]}...")  # Log parcial para evitar poluição

        # Se for uma consulta SQL válida
        if resposta_ia.strip().upper().startswith("SELECT"):
            if not validar_consulta_sql(resposta_ia):
                raise HTTPException(
                    status_code=400,
                    detail="Consulta SQL gerada não é segura"
                )
            
            logging.info(f"Executando consulta SQL validada: {resposta_ia}")
            conn = None
            try:
                conn = conectar_banco()
                cursor = conn.cursor()
                
                cursor.execute(resposta_ia)
                resultado = cursor.fetchall()
                
                if resultado:
                    # Formata a resposta de acordo com a consulta
                    if len(resultado[0]) == 1:
                        resposta = str(resultado[0][0])
                    else:
                        resposta = ", ".join(str(item) for item in resultado[0])
                    
                    return {
                        "pergunta": request.pergunta,
                        "resposta": resposta,
                        "tipo": "dados_banco"
                    }
                else:
                    return {
                        "pergunta": request.pergunta,
                        "resposta": "Nenhum dado encontrado para a consulta.",
                        "tipo": "sem_resultados"
                    }
            except psycopg2.Error as e:
                logging.error(f"Erro no banco de dados: {e}")
                raise HTTPException(
                    status_code=400,
                    detail=f"Erro na consulta SQL: {str(e)}"
                )
            finally:
                if conn:
                    conn.close()
        
        # Se for uma resposta direta da IA
        return {
            "pergunta": request.pergunta,
            "resposta": resposta_ia,
            "tipo": "resposta_direta"
        }

    except HTTPException:
        raise  # Re-lança exceções HTTP já tratadas
    except Exception as e:
        logging.error(f"Erro inesperado: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Erro interno ao processar a solicitação"
        )