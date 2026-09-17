from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import whois
import requests
from datetime import datetime
import re

# 1. A variável 'app' PRECISA ser criada antes de qualquer decorador (@app...)
app = FastAPI(
    title="Verificador de Reputação de Empresas",
    description="API para verificar a confiabilidade de e-commerces.",
    version="0.2.0"
)

# 2. Definição do Modelo de Dados
class EmpresaRequest(BaseModel):
    url: str
    cnpj: str | None = None

# 3. Funções Auxiliares
def consultar_whois_dominio(dominio: str):
   from datetime import datetime, timezone

def consultar_whois_dominio(dominio: str):
    """Consulta a data de criação do domínio e calcula a idade em dias."""
    try:
        dados_whois = whois.whois(dominio)
        data_criacao = dados_whois.creation_date
        
        if isinstance(data_criacao, list):
            data_criacao = data_criacao[0]
            
        if not data_criacao:
            return {"idade_dias": 0, "data_criacao": None, "alerta": "Data não encontrada"}
            
        # Normaliza as datas removendo a informação de fuso horário para permitir a subtração segura
        if data_criacao.tzinfo is not None:
            data_criacao = data_criacao.replace(tzinfo=None)
            
        hoje = datetime.now().replace(tzinfo=None)
        idade_dias = (hoje - data_criacao).days
        
        return {
            "idade_dias": idade_dias,
            "data_criacao": data_criacao.strftime("%Y-%m-%d"),
            "alerta": None
        }
    except Exception as e:
        return {"idade_dias": 0, "data_criacao": None, "alerta": str(e)}

def consultar_cnpj_brasilapi(cnpj: str):
    """Consulta a situação cadastral do CNPJ na Receita Federal via BrasilAPI."""
    cnpj_limpo = re.sub(r'\D', '', cnpj)
    
    if len(cnpj_limpo) != 14:
        return {"valido": False, "erro": "CNPJ deve conter 14 dígitos."}
        
    url = f"https://brasilapi.com.br/api/cnpj/v1/{cnpj_limpo}"
    
    try:
        resposta = requests.get(url, timeout=5)
        if resposta.status_code == 200:
            dados = resposta.json()
            return {
                "valido": True,
                "razao_social": dados.get("razao_social"),
                "nome_fantasia": dados.get("nome_fantasia"),
                "situacao_cadastral": dados.get("descricao_situacao_cadastral"),
                "data_inicio_atividade": dados.get("data_inicio_atividade")
            }
        elif resposta.status_code == 404:
            return {"valido": False, "erro": "CNPJ não encontrado na Receita Federal."}
        else:
            return {"valido": False, "erro": "Serviço da Receita temporariamente indisponível."}
    except Exception as e:
        return {"valido": False, "erro": f"Falha na conexão: {str(e)}"}

# 4. Rotas da Aplicação (Agora o @app vai funcionar porque 'app' já existe acima)
@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Verificador de Confiabilidade</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f4f4f9; }
            .card { background: white; padding: 20px; border-radius: 8px; max-width: 500px; margin: auto; }
            input, button { padding: 10px; margin-top: 10px; width: 100%; box-sizing: border-box; }
            button { background: #28a745; color: white; border: none; font-weight: bold; cursor: pointer; }
        </style>
    </head>
    <body>
        <div class="card">
            <h2>Verificar Empresa</h2>
            <input type="text" id="url" placeholder="Digite o site (ex: google.com)">
            <input type="text" id="cnpj" placeholder="Digite o CNPJ (opcional)">
            <button onclick="analisar()">Analisar Confiabilidade</button>
            <div id="resultado" style="margin-top:20px;"></div>
        </div>

        <script>
            async function analisar() {
                const url = document.getElementById('url').value;
                const cnpj = document.getElementById('cnpj').value;
                const res = await fetch('/analisar', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({url: url, cnpj: cnpj})
                });
                const dados = await res.json();
                document.getElementById('resultado').innerHTML = 
                    `<h3>Resultado: ${dados.status_risco}</h3>
                     <p>Score: <b>${dados.score_confianca}/100</b></p>
                     <p>${dados.alertas.join('<br>')}</p>`;
            }
        </script>
    </body>
    </html>
    """

@app.post("/analisar")
def analisar_empresa(dados: EmpresaRequest):
    dominio_limpo = dados.url.replace("https://", "").replace("http://", "").replace("www.", "").split("/")[0]
    info_dominio = consultar_whois_dominio(dominio_limpo)
    
    info_cnpj = None
    if dados.cnpj:
        info_cnpj = consultar_cnpj_brasilapi(dados.cnpj)

    score = 0
    alertas = []
    
    idade = info_dominio["idade_dias"]
    if idade > 365:
        score += 50
    elif idade > 90:
        score += 25
        alertas.append("Domínio recente (menos de 1 ano).")
    else:
        alertas.append("ALERTA CRÍTICO: Domínio criado há menos de 90 dias!")

    if info_cnpj:
        if info_cnpj.get("valido") and info_cnpj.get("situacao_cadastral") == "ATIVA":
            score += 50
        else:
            alertas.append("CNPJ inativo, suspenso ou não encontrado!")
    else:
        score += 20
        alertas.append("CNPJ não fornecido para validação.")

    if score >= 80:
        status = "BAIXO RISCO"
    elif score >= 50:
        status = "MÉDIO RISCO"
    else:
        status = "ALTO RISCO"

    return {
        "dominio": dominio_limpo,
        "score_confianca": score,
        "status_risco": status,
        "alertas": alertas,
        "detalhes": {
            "whois": info_dominio,
            "cnpj": info_cnpj
        }
    }