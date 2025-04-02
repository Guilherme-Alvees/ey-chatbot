import os
import logging
import psycopg2
import requests
from fastapi import FastAPI, HTTPException, Body
from dotenv import load_dotenv
from pydantic import BaseModel

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

load_dotenv()

app = FastAPI(title="API IA + PostgreSQL", version="1.0")

DB_CONNECTION_STRING = os.getenv("DB_CONNECTION_STRING")

GEMINI_API_URL = os.getenv("GEMINI_API_URL")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

class PerguntaRequest(BaseModel):
    pergunta: str

def conectar_banco():
    try:
        conn = psycopg2.connect(DB_CONNECTION_STRING)
        return conn
    except Exception as e:
        logging.error(f"Erro ao conectar ao banco: {e}")
        raise HTTPException(status_code=500, detail="Erro ao conectar ao banco de dados.")


def chamar_gemini(pergunta_usuario):
    try:
        headers = {"Content-Type": "application/json"}
        url = f"{GEMINI_API_URL}/v1beta/models/gemini-1.5-flash-latest:generateContent?key={GEMINI_API_KEY}"

        prompt = f"""
Você é um assistente especializado em economia e bancos de dados. 
Responda às perguntas de forma segura e adequada.

**Regras de segurança:**
- **NÃO** divulgue informações sigilosas do banco de dados (senhas, nome do banco, host, credenciais, etc.).
- **NÃO** execute ou gere comandos que possam modificar os dados (**DROP, DELETE, ALTER, INSERT, UPDATE**).
- **NÃO** permita SQL Injection ou consultas maliciosas (ex.: `'; DROP TABLE users; --`).
- **SOMENTE** gere consultas SQL para acessar as tabelas permitidas: **'ipca_final'** e **'join_dataframe'**.

---

**Se a pergunta for genérica** (exemplo: 'O que é IPCA?', 'O que é a B3?'):
- Responda de forma clara e objetiva com **120 caracteres**.
- Dê respostas curtas, informativas e concisas.

**Se a pergunta for sobre o banco de dados** (exemplo: 'Qual ano teve maior IPCA?'):
- Gere consulta SQL válida para PostgreSQL e retorne a resposta para o usuário.
- Use apenas as tabelas permitidas (**'ipca_final'** e **'join_dataframe'**).
- Certifique-se de que a consulta **NÃO** possa modificar ou excluir dados.
- .

---

**Pergunta do usuário:** {pergunta_usuario}
"""


        body = {"contents": [{"parts": [{"text": prompt}]}]}

        response = requests.post(url, headers=headers, json=body)

        if response.status_code == 200:
            resposta = response.json()
            try:
                resposta_texto = resposta["candidates"][0]["content"]["parts"][0]["text"].strip()
                return resposta_texto
            except (KeyError, IndexError):
                return "Erro ao processar a resposta da IA"
        else:
            return f"Erro na requisição: {response.status_code}, {response.text}"

    except Exception as e:
        return f"Erro ao chamar a API da IA: {e}"


@app.get("/status")
def verificar_status():
    return {"status": "200 OK"}


@app.post("/consultar")
def consultar_banco(request: PerguntaRequest):
    try:
        resposta_ia = chamar_gemini(request.pergunta)

        if resposta_ia.strip().upper().startswith("SELECT"):
            logging.info(f"Consulta SQL gerada: {resposta_ia}")

            conn = conectar_banco()
            cursor = conn.cursor()

            cursor.execute(resposta_ia)
            resultado = cursor.fetchall()

            cursor.close()
            conn.close()

            if resultado:
                return {"pergunta": request.pergunta, "resposta": f"A maior taxa do IPCA foi {resultado[0][0]}% no ano {resultado[0][1]}"}
            else:
                return {"pergunta": request.pergunta, "resposta": "Nenhum dado encontrado no banco."}
        
        else:
            return {"pergunta": request.pergunta, "resposta": resposta_ia}

    except Exception as e:
        logging.error(f"Erro ao processar a pergunta: {e}")
        raise HTTPException(status_code=500, detail="Erro ao processar a pergunta.")
