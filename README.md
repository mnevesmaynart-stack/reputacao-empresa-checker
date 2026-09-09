# reputacao-empresa-checker
Sistema de Inteligência Artificial/Ferramenta de Software para verificar a confiabilidade das empresas utilizando algumas fontes de dados como base.

reputacao-empresa-checker/
├── .github/
│   └── workflows/
│       └── ci.yml             # Testes automáticos da API
├── backend/
│   ├── app/
│   │   ├── api/               # Endpoints REST (FastAPI/Node)
│   │   ├── collectors/        # Scrapers (Reclame Aqui, WHOIS, CNPJ)
│   │   ├── services/          # Módulo de IA (Análise de Sentimento/LLM)
│   │   └── main.py
│   ├── requirements.txt
│   └── Dockerfile
├── extension/                 # Extensão para Chrome/Edge
│   ├── manifest.json
│   ├── popup.html
│   └── content.js
├── docker-compose.yml
└── README.md
