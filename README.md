# Sistema de Análise Automatizada de Imóveis

## Visão Geral
Sistema para análise automatizada de imóveis em leilão, integrando dados geográficos, jurídicos, de mercado e ambientais para fornecer insights valiosos para investidores.

## Estado Atual do Projeto

### Funcionalidades Implementadas
1. **Extração de Dados**
   - Template para MegaLeilões
   - Validação de URLs e documentos
   - Cache de análises
   - Extração de dados básicos do imóvel

2. **Análise de Dados**
   - Análise geográfica básica
   - Integração com IBGE para dados municipais
   - Sistema de validação de dados
   - Geração de recomendações básicas

3. **Infraestrutura**
   - API REST com Flask
   - Sistema de logs
   - Monitoramento básico
   - Cache de resultados

### Problemas Conhecidos
1. **Servidor Flask**
   - Instabilidade no modo debug
   - Problemas de porta em uso
   - Necessidade de reinicialização frequente

2. **Integrações**
   - Falta de implementação completa das APIs de mercado e jurídica
   - Dependência de chaves de API externas
   - Necessidade de alternativas para APIs pagas

3. **Análise de Dados**
   - Endereços vazios retornando dados padrão
   - Falta de validação mais robusta
   - Necessidade de mais fontes de dados

## Prioridades Pendentes

### Alta Prioridade
1. **Correção de Bugs**
   - Resolver instabilidade do servidor Flask
   - Implementar tratamento adequado para endereços vazios
   - Corrigir problemas de cache

2. **Integrações**
   - Implementar alternativas para APIs pagas
   - Melhorar integração com IBGE
   - Adicionar mais fontes de dados públicas

3. **Análise de Dados**
   - Implementar análise de mercado mais robusta
   - Adicionar análise jurídica completa
   - Melhorar sistema de recomendações

### Média Prioridade
1. **Infraestrutura**
   - Implementar sistema de filas para processamento assíncrono
   - Melhorar sistema de cache
   - Adicionar mais testes automatizados

2. **Interface**
   - Melhorar documentação da API
   - Adicionar endpoints para monitoramento
   - Implementar sistema de métricas

3. **Segurança**
   - Implementar autenticação
   - Adicionar rate limiting
   - Melhorar validação de inputs

### Baixa Prioridade
1. **Melhorias**
   - Adicionar mais templates para diferentes sites
   - Implementar análise de imagens
   - Adicionar suporte a mais tipos de documentos

2. **Documentação**
   - Criar guia de contribuição
   - Adicionar exemplos de uso
   - Documentar arquitetura

## Próximos Passos Imediatos
1. Resolver problemas de instabilidade do servidor
2. Implementar alternativas para APIs pagas
3. Melhorar sistema de análise de dados
4. Adicionar mais testes automatizados

## Requisitos Técnicos
- Python 3.11+
- Flask
- Requests
- NumPy
- Pandas
- Outras dependências listadas em requirements.txt

## Configuração
1. Clone o repositório
2. Crie um ambiente virtual
3. Instale as dependências
4. Configure as variáveis de ambiente
5. Execute o servidor Flask

## Contribuição
Contribuições são bem-vindas! Por favor, siga as diretrizes de contribuição e código de conduta.

## Licença
Este projeto está licenciado sob a licença MIT.

## APIs Utilizadas

O sistema integra-se com várias APIs para coletar e processar dados. Abaixo está a lista detalhada das APIs utilizadas:

### APIs de Dados Jurídicos
- **API Judicial**: Integração com dados de processos judiciais
  - Endpoint: `https://api.judicial.com/processos/{numero_processo}`
  - Requer chave de API: `LEGAL_API_KEY`
  - Status: Aguardando acesso

### APIs de Dados de Mercado
- **API Imobiliária**: Dados de mercado imobiliário
  - Endpoint: `https://api.imobiliaria.com/mercado`
  - Requer chave de API: `MARKET_API_KEY`
  - Status: Aguardando acesso

### APIs de Dados Geográficos
- **Google Maps API**: Geocodificação e dados de localização
  - Endpoint: `https://maps.googleapis.com/maps/api/geocode/json`
  - Requer chave de API: `GOOGLE_MAPS_API_KEY`
  - Status: Implementado

- **OpenStreetMap API**: Dados de localização e pontos de interesse
  - Endpoint: `https://nominatim.openstreetmap.org`
  - Não requer chave de API
  - Status: Implementado

### APIs de Dados Públicos
- **ViaCEP**: Consulta de endereços por CEP
  - Endpoint: `https://viacep.com.br/ws/{cep}/json`
  - Não requer chave de API
  - Status: Implementado

- **IBGE API**: Dados demográficos e econômicos
  - Endpoint: `https://servicodados.ibge.gov.br/api/v1`
  - Não requer chave de API
  - Status: Implementado

- **Banco Central API**: Dados econômicos e financeiros
  - Endpoint: `https://api.bcb.gov.br/dados/serie/bcdata.sgs`
  - Não requer chave de API
  - Status: Implementado

### Configuração de Chaves de API
Para utilizar as APIs que requerem autenticação, é necessário configurar as seguintes variáveis de ambiente no arquivo `.env`:

```env
LEGAL_API_KEY=sua_chave_aqui
MARKET_API_KEY=sua_chave_aqui
GOOGLE_MAPS_API_KEY=sua_chave_aqui
```
