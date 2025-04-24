import pytest
from flask import Flask
from flask_app import app
from unittest.mock import patch, MagicMock

@pytest.fixture
def client():
    """Fixture que cria um cliente de teste para a aplicação Flask."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_home_route(client):
    """Testa a rota principal."""
    response = client.get('/')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'ok'
    assert 'API está funcionando' in data['message']

def test_test_route_with_valid_data(client):
    """Testa a rota de teste com dados válidos."""
    response = client.post('/test', json={'message': 'teste'})
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'success'
    assert data['received_message'] == 'teste'

def test_test_route_with_invalid_data(client):
    """Testa a rota de teste com dados inválidos."""
    response = client.post('/test', data='invalid')
    assert response.status_code == 500

def test_analisar_imovel_with_valid_data(client):
    """Testa a rota de análise com dados válidos."""
    valid_data = {
        'endereco': 'Rua Teste, 123',
        'area': 100,
        'tipo': 'Apartamento',
        'valor_mercado': 500000,
        'valor_minimo_leilao': 400000
    }
    
    with patch('flask_app.AnaliseImovel') as mock_analise:
        mock_instance = mock_analise.return_value
        mock_instance.gerar_analise.return_value = {'test': 'result'}
        
        response = client.post('/analisar_imovel', json=valid_data)
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'success'
        assert 'analise' in data

def test_analisar_imovel_with_missing_fields(client):
    """Testa a rota de análise com campos faltantes."""
    invalid_data = {
        'endereco': 'Rua Teste, 123',
        'area': 100
    }
    
    response = client.post('/analisar_imovel', json=invalid_data)
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data
    assert 'campos' in data

def test_analisar_imovel_with_invalid_values(client):
    """Testa a rota de análise com valores inválidos."""
    invalid_data = {
        'endereco': 'Rua Teste, 123',
        'area': 100,
        'tipo': 'Apartamento',
        'valor_mercado': 'invalid',
        'valor_minimo_leilao': 400000
    }
    
    response = client.post('/analisar_imovel', json=invalid_data)
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data

def test_cache_maintenance_route(client):
    """Testa a rota de manutenção do cache."""
    with patch('flask_app.cache_manager.clear_expired_cache') as mock_clear:
        response = client.post('/cache/maintenance?action=clean')
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'success'
        mock_clear.assert_called_once()

def test_cache_maintenance_route_with_invalid_action(client):
    """Testa a rota de manutenção do cache com ação inválida."""
    response = client.post('/cache/maintenance?action=invalid')
    assert response.status_code == 400
    data = response.get_json()
    assert data['status'] == 'error' 