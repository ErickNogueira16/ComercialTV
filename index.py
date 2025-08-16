from flask import Flask, render_template_string
import jwt
import datetime
import uuid
import gunicorn

app = Flask(__name__)

connectedAppClientId = "413bb233-2b39-4e2a-a42b-400779d2ce80"
connectedAppSecretKey = "Y33AkudE1IM0xY5KDzVDVmAZB+89fq7EY3Ygc3qD7Vk="
connectedAppSecretId = "9c456f30-e177-46e9-93fb-f1478c03410e"
user = "anabeatriz@raizzcapital.com.br"

viz_url = "https://us-east-1.online.tableau.com/t/anabeatriz-8787706e44/views/TVComercial-RaizzCapital_17543562925950/ResumoDemandaQuente?:origin=card_share_link&:embed=y"

# --- Geração do JWT ---
def generate_jwt():
    token1 = jwt.encode(
        {
            "iss": connectedAppClientId,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=5),
            "jti": str(uuid.uuid4()),
            "aud": "tableau",
            "sub": user,
            "scp": ["tableau:views:embed"]
        },
        connectedAppSecretKey,
        algorithm="HS256",
        headers={
            "kid": connectedAppSecretId,
            "iss": connectedAppClientId
        }
    )
    return token1

@app.route('/')
def index():
    token = generate_jwt()

    html_str = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Raizz Capital - TV Comercial</title>
        <script type="text/javascript" src="https://public.tableau.com/javascripts/api/tableau-2.min.js"></script>
        <style>
            * {{ margin: 0; padding: 0; }}
            #vizContainer {{ width: 100%; height: 100vh; }}
        </style>
        <link rel="icon" href="https://raizzcapital.com.br/wp-content/uploads/2024/02/logo-raizz-capital-fundo-branco.webp">
    </head>
    <body>
        <div id="vizContainer"></div>
        <script>
            let viz;
            const dashboardNames = ["Resumo | Demanda Quente", "Funil | Visitas", "Setores | Imobiliárias", "Tamanho da Demanda"];
            const produtos = ["Raizz Viana", "Raizz Itajaí"];
            
            const tempoPorPainel = 10000;
            let currentDashboardIndex = 0;
            let currentProdutoIndex = 0;
            let isFirstRun = true;

            const url = "{viz_url}";

            const options = {{
                hideTabs: true,
                hideToolbar: true,
                onFirstInteractive: function() {{
                    console.log("Visualização carregada!");
                    iniciarCiclo();
                }},
                headers: {{
                    "Authorization": "Bearer {token}"
                }}
            }};

            function initViz() {{
                const containerDiv = document.getElementById("vizContainer");
                viz = new tableau.Viz(containerDiv, url, options);
            }}

            function iniciarCiclo() {{
                trocarProdutoEPainel();
                setInterval(trocarProdutoEPainel, tempoPorPainel);
            }}

            function trocarProdutoEPainel() {{
                const workbook = viz.getWorkbook();
                const produtoAtual = produtos[currentProdutoIndex];
                const painelAtual = dashboardNames[currentDashboardIndex];

                if(isFirstRun) {{
                    workbook.activateSheetAsync(painelAtual)
                        .then(() => {{
                            console.log("Painel inicial ativado:", painelAtual);
                            isFirstRun = false;
                        }});
                    return;
                }}

                workbook.changeParameterValueAsync("ProdutoSelecionado", produtoAtual)
                    .then(() => {{
                        console.log("Produto definido para:", produtoAtual);
                        return workbook.activateSheetAsync(painelAtual);
                    }})
                    .then(() => {{
                        console.log("Painel ativado:", painelAtual);
                        currentDashboardIndex++;
                        if(currentDashboardIndex >= dashboardNames.length) {{
                            currentDashboardIndex = 0;
                            currentProdutoIndex = (currentProdutoIndex + 1) % produtos.length;
                        }}
                    }})
                    .catch(error => {{
                        console.error("Erro na transição:", error);
                    }});
            }}

            initViz();

            // Recarrega a cada 15 min
            setTimeout(() => {{ location.reload(); }}, 900000);
        </script>
    </body>
    </html>
    """
    return html_str

if __name__ == '__main__':
    app.run(debug=True)
