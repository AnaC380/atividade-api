import os
import requests
import hashlib
from datetime import datetime
from dotenv import load_dotenv

# Carrega variáveis do .env
load_dotenv()

class APICidades:
    def __init__(self):
        self.base_url = os.getenv('API_BASE_URL')
        self.email = os.getenv('API_EMAIL')
        self.senha = os.getenv('API_SENHA')
        self.nome = os.getenv('NOME_COMPLETO')
        self.ra = os.getenv('RA')
        
        if not all([self.base_url, self.email, self.senha]):
            raise ValueError("Variáveis de ambiente não configuradas corretamente")

    def gerar_contra_senha(self):
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        return hashlib.sha256(f"{self.email}{self.senha}{timestamp}".encode()).hexdigest()

    def autenticar(self):
        contra_senha = self.gerar_contra_senha()
        response = requests.post(
            f"{self.base_url}/login",
            json={
                "email": self.email,
                "password": self.senha,
                "contra_senha": contra_senha
            }
        )
        if response.status_code == 200:
            return response.json().get('token'), contra_senha
        raise Exception(f"Falha na autenticação: {response.text}")

    def obter_cidades(self, token):
        response = requests.get(
            f"{self.base_url}/cidades",
            headers={"x-access-token": token}
        )
        if response.status_code == 200:
            return response.json()
        raise Exception(f"Erro ao obter cidades: {response.text}")

    def gerar_relatorio(self, cidades, token, contra_senha):
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Relatório API Cidades</title>
    <style>
        body {{ font-family: Arial; margin: 20px; }}
        table {{ border-collapse: collapse; width: 80%; margin: 20px auto; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
        .info {{ margin-bottom: 30px; }}
    </style>
</head>
<body>
    <div class="info">
        <h2>Dados do Aluno</h2>
        <p><strong>Nome:</strong> {self.nome}</p>
        <p><strong>RA:</strong> {self.ra}</p>
    </div>
    
    <div class="info">
        <h2>Dados da API</h2>
        <p><strong>Contra-senha:</strong> {contra_senha}</p>
        <p><strong>Token:</strong> {token}</p>
    </div>
    
    <h2 style="text-align: center;">5 Cidades Obtidas</h2>
    <table>
        <tr><th>ID</th><th>Nome</th></tr>
        {"".join(f"<tr><td>{c['id']}</td><td>{c['nome']}</td></tr>" for c in cidades[:5])}
    </table>
</body>
</html>"""
        
        with open('relatorio_cidades.html', 'w', encoding='utf-8') as f:
            f.write(html)
        print("Relatório HTML gerado: relatorio_cidades.html")

def main():
    try:
        api = APICidades()
        print("Autenticando na API...")
        token, contra_senha = api.autenticar()
        
        print("\nObtendo lista de cidades...")
        cidades = api.obter_cidades(token)
        
        print("\nGerando relatório...")
        api.gerar_relatorio(cidades, token, contra_senha)
        
        print("\nDados importantes para o relatório:")
        print(f"Nome: {api.nome}")
        print(f"RA: {api.ra}")
        print(f"Token: {token}")
        print(f"Contra-senha: {contra_senha}")
        print("\nPrimeiras 5 cidades:")
        for cidade in cidades[:5]:
            print(f"ID: {cidade['id']} - Nome: {cidade['nome']}")
            
    except Exception as e:
        print(f"\nErro: {str(e)}")
        input("Pressione Enter para sair...")
        exit(1)

if __name__ == "__main__":
    main()