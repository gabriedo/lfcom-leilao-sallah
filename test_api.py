import requests
import json

# Carrega os dados de teste
with open('test_data.json', 'r') as f:
    test_data = json.load(f)

# Faz a requisição para a API
try:
    response = requests.post(
        'http://localhost:8000/analisar_imovel/',
        json=test_data,
        headers={'Content-Type': 'application/json'}
    )
    
    # Imprime a resposta
    print('Status Code:', response.status_code)
    print('Response:', response.json())
    
except requests.exceptions.ConnectionError:
    print("Erro: Não foi possível conectar ao servidor. Verifique se o servidor está rodando.") 