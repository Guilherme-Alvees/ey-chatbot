#  API FastAPI

Este é um projeto de API construído com FastAPI, integrando a IA do Google Gemini para consultas SQL em um banco de dados PostgreSQL.

## Como configurar o ambiente
- É necessário ter o GIT e o Python instalados na máquina

### 1. Clone este repositório
Primeiro, clone o repositório para a sua máquina local:
```
git init

git clone https://github.com/Guilherme-Alvees/ey-chatbot.git

cd ey-chatbot

cd api
```

### 2. Crie um ambiente virtual
Crie um ambiente virtual Python dentro do diretório do projeto:
```
python -m venv .venv
```

### 3. Ative o ambiente virtual
- No Windows:
```
.\.venv\Scripts\activate
```
- No macOS/Linux:
```
source .venv/bin/activate
```

### 4. Instale as dependências
Com o ambiente virtual ativado, instale as dependências do projeto listadas no arquivo 'requirements.txt':
```
pip install -r requirements.txt
```

### 5. Acesse a API
Rode o seguinte comando no terminal dentro do path '/ey-chatbot'
```
uvicorn api:app --reload
```
Deve aparece algo como isso em seu terminal:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [32516] using StatReload
INFO:     Started server process [17880]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### 6. Testar a API
Para testar a API, você pode acessar seu navegador e colocar o seguinte enderço na barra de pesquisa superior, se trata de um endpoint do tipo GET
```
http://127.0.0.1:8000/status
```
Deverá retornar uma mensagem JSON igual a essa:
```
{
  "status": "200 OK"
}
```
