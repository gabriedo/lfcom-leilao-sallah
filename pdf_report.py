from weasyprint import HTML, CSS
from jinja2 import Template
import os
from datetime import datetime
from typing import Dict, Any
from config import logger

# Template HTML para o relatório
REPORT_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 2cm;
            line-height: 1.6;
            color: #333;
        }
        .header {
            text-align: center;
            margin-bottom: 2cm;
            border-bottom: 2px solid #2c3e50;
            padding-bottom: 1cm;
        }
        .section {
            margin-bottom: 1.5cm;
            padding: 1cm;
            background-color: #f9f9f9;
            border-radius: 5px;
        }
        .section-title {
            font-size: 1.3em;
            font-weight: bold;
            margin-bottom: 0.8cm;
            color: #2c3e50;
            border-bottom: 1px solid #ddd;
            padding-bottom: 0.3cm;
        }
        .info-item {
            margin-bottom: 0.5cm;
            display: flex;
            justify-content: space-between;
        }
        .info-label {
            font-weight: bold;
            color: #555;
        }
        .info-value {
            color: #2c3e50;
        }
        .highlight {
            color: #e74c3c;
            font-weight: bold;
        }
        .warning {
            background-color: #fff3cd;
            padding: 0.5cm;
            border-radius: 3px;
            margin: 0.5cm 0;
        }
        .footer {
            margin-top: 2cm;
            text-align: center;
            font-size: 0.8em;
            color: #7f8c8d;
            border-top: 1px solid #ddd;
            padding-top: 1cm;
        }
        .status-badge {
            padding: 0.2cm 0.5cm;
            border-radius: 3px;
            font-weight: bold;
            display: inline-block;
        }
        .status-success {
            background-color: #d4edda;
            color: #155724;
        }
        .status-warning {
            background-color: #fff3cd;
            color: #856404;
        }
        .status-danger {
            background-color: #f8d7da;
            color: #721c24;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>Relatório de Análise de Imóvel</h1>
        <p>Data: {{ data_analise }}</p>
    </div>

    <div class="section">
        <div class="section-title">Informações do Imóvel</div>
        <div class="info-item">
            <span class="info-label">Endereço:</span>
            <span class="info-value">{{ dados_imovel.endereco }}</span>
        </div>
        <div class="info-item">
            <span class="info-label">Área:</span>
            <span class="info-value">{{ dados_imovel.area }} m²</span>
        </div>
        <div class="info-item">
            <span class="info-label">Tipo:</span>
            <span class="info-value">{{ dados_imovel.tipo }}</span>
        </div>
    </div>

    <div class="section">
        <div class="section-title">Análise Jurídica</div>
        <div class="info-item">
            <span class="info-label">Penhora/Gravames:</span>
            <span class="info-value status-{{ 'danger' if resumo_juridico.penhora == 'sim' else 'success' }}">
                {{ resumo_juridico.penhora }}
            </span>
        </div>
        <div class="info-item">
            <span class="info-label">Dívidas de Condomínio:</span>
            <span class="info-value status-{{ 'warning' if resumo_juridico.dividas_condominio == 'sim' else 'success' }}">
                {{ resumo_juridico.dividas_condominio }}
            </span>
        </div>
        <div class="info-item">
            <span class="info-label">Ocupação:</span>
            <span class="info-value status-{{ 'warning' if resumo_juridico.ocupado == 'sim' else 'success' }}">
                {{ resumo_juridico.ocupado }}
            </span>
        </div>
        {% if resumo_juridico.observacoes %}
        <div class="warning">
            <strong>Observações:</strong> {{ resumo_juridico.observacoes }}
        </div>
        {% endif %}
    </div>

    <div class="section">
        <div class="section-title">Análise Financeira</div>
        <div class="info-item">
            <span class="info-label">Valor de Mercado:</span>
            <span class="info-value">R$ {{ "%.2f"|format(dados_imovel.valor_mercado) }}</span>
        </div>
        <div class="info-item">
            <span class="info-label">Valor Mínimo do Leilão:</span>
            <span class="info-value">R$ {{ "%.2f"|format(dados_imovel.valor_minimo_leilao) }}</span>
        </div>
        <div class="info-item">
            <span class="info-label">Margem Financeira:</span>
            <span class="info-value status-{{ 'success' if margem_financeira > 20 else 'warning' }}">
                {{ "%.2f"|format(margem_financeira) }}%
            </span>
        </div>
    </div>

    <div class="footer">
        <p>Relatório gerado automaticamente pelo sistema LFCOM</p>
        <p>Este relatório é confidencial e destinado apenas ao uso interno</p>
    </div>
</body>
</html>
"""

def generate_pdf_report(
    juridical_analysis: Dict,
    financial_margin: float,
    property_data: Dict[str, Any]
) -> str:
    """
    Gera um relatório PDF com base nos dados analisados.
    """
    try:
        # Prepara os dados para o template
        template_data = {
            "data_analise": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "resumo_juridico": juridical_analysis,
            "margem_financeira": financial_margin,
            "dados_imovel": property_data
        }
        
        # Renderiza o template
        template = Template(REPORT_TEMPLATE)
        html_content = template.render(**template_data)
        
        # Gera o PDF
        pdf_filename = f"relatorio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        pdf_path = os.path.join(REPORTS_DIR, pdf_filename)
        
        HTML(string=html_content).write_pdf(pdf_path)
        
        logger.info(f"Relatório PDF gerado com sucesso: {pdf_path}")
        return pdf_path
        
    except Exception as e:
        logger.error(f"Erro ao gerar relatório PDF: {str(e)}")
        raise 