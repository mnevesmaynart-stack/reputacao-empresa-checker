from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

# Rota para abrir a página inicial do seu site no navegador
@app.get("/", response_class=HTMLResponse)
def pagina_inicial():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Verificador de Confiabilidade de Lojas</title>
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
            <input type="text" id="url" placeholder="Digite o site (ex: lojaexemplo.com.br)">
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