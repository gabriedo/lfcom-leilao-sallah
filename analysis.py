import os
from typing import Dict, Optional
from openai_client import openai_client

async def analyze_property(edital_texto: Optional[str] = None, matricula_texto: Optional[str] = None) -> Dict:
    """
    Analisa os documentos do imóvel usando GPT-4 para extrair informações críticas.
    """
    if not edital_texto and not matricula_texto:
        return {
            "penhora": "não informado",
            "dividas_condominio": "não informado",
            "ocupado": "não informado",
            "observacoes": "Nenhum documento fornecido para análise."
        }

    # Prepara o prompt para o GPT-4
    prompt = f"""
    Analise os seguintes documentos de um imóvel em leilão e extraia as seguintes informações:
    
    Documentos fornecidos:
    Edital: {edital_texto or 'Não fornecido'}
    Matrícula: {matricula_texto or 'Não fornecido'}
    
    Por favor, identifique e retorne APENAS as seguintes informações em formato JSON:
    1. Se há penhoras ou gravames (sim/não)
    2. Se há dívidas de condomínio (sim/não)
    3. Se o imóvel está ocupado (sim/não)
    4. Observações relevantes sobre condições e riscos jurídicos
    
    Retorne APENAS o JSON, sem texto adicional.
    """

    try:
        response = await openai_client.client.chat.completions.create(
            model=openai_client.model,
            messages=[
                {"role": "system", "content": "Você é um especialista em análise de documentos imobiliários."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            max_tokens=500
        )

        # Extrai e retorna a análise
        analysis = response.choices[0].message.content
        return eval(analysis)  # Converte a string JSON em dicionário

    except Exception as e:
        return {
            "penhora": "erro",
            "dividas_condominio": "erro",
            "ocupado": "erro",
            "observacoes": f"Erro na análise: {str(e)}"
        }

def calculate_financial_margin(valor_mercado: float, valor_minimo_leilao: float) -> float:
    """
    Calcula a margem financeira percentual entre o valor de mercado e o valor mínimo do leilão.
    """
    if valor_mercado <= 0 or valor_minimo_leilao <= 0:
        raise ValueError("Valores devem ser positivos")
    
    margem = ((valor_mercado - valor_minimo_leilao) / valor_mercado) * 100
    return round(margem, 2) 