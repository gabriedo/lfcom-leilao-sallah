from typing import Dict, Any, List, Optional
import logging
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
from .base_template import LeilaoTemplate
from openai import OpenAI
import os
import random
import time
import pytesseract
from PIL import Image
from io import BytesIO
import numpy as np
import cv2

class SmartTemplate(LeilaoTemplate):
    """Template inteligente capaz de extrair dados de diferentes sites de leilão"""
    
    def __init__(self):
        """Inicializa o template inteligente"""
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.openai_client = None
        if os.getenv('OPENAI_API_KEY'):
            self.openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        # Configura o caminho do Tesseract (ajuste conforme necessário)
        if os.getenv('TESSERACT_PATH'):
            pytesseract.pytesseract.tesseract_cmd = os.getenv('TESSERACT_PATH')
        
        # Padrões regex mais flexíveis
        self.patterns = {
            'valor': r'R\$\s*[\d.,]+(?:\s*mil|\s*milhões)?|\d+[.,]\d+(?:\s*mil|\s*milhões)?',
            'area': r'\d+[.,]?\d*\s*(?:m²|metros quadrados|m2)',
            'matricula': r'(?:matrícula|registro)\s*(?:n[°º.]?)?\s*\d+',
            'processo': r'\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}|\d{20}|\d{25}',
            'data': r'\d{2}[/-]\d{2}[/-]\d{4}|\d{1,2}\s+(?:de\s+)?(?:janeiro|fevereiro|março|abril|maio|junho|julho|agosto|setembro|outubro|novembro|dezembro)\s+(?:de\s+)?\d{4}'
        }
        
        # Tipos de arquivos suportados
        self.tipos_imagem = ['.jpg', '.jpeg', '.png', '.webp', '.gif']
        self.tipos_documento = ['.pdf', '.doc', '.docx', '.txt']
        
        # Cache para OCR
        self._ocr_cache = {}
        
    def validar_url(self, url: str) -> bool:
        """Verifica se a URL é válida e pertence a um site de leilão"""
        try:
            if not url or not url.startswith(('http://', 'https://')):
                return False
                
            # Palavras-chave comuns em sites de leilão
            keywords = ['leilao', 'leilão', 'hasta', 'praça', 'judicial', 'extrajudicial']
            return any(keyword in url.lower() for keyword in keywords)
            
        except Exception as e:
            self.logger.error(f"Erro ao validar URL: {str(e)}")
            return False
            
    def extrair_dados(self, url: str) -> Dict[str, Any]:
        """Extrai dados do imóvel usando técnicas inteligentes de scraping com fallback"""
        try:
            self.logger.info(f"Iniciando extração inteligente de dados da URL: {url}")
            
            # Obtém o conteúdo da página
            response = self._fazer_requisicao(url)
            if not response:
                return {'erro': 'Falha ao acessar a URL'}
                
            # Parse do HTML
            soup = BeautifulSoup(response, 'html.parser')
            
            # Remove elementos irrelevantes
            for tag in soup(['script', 'style', 'nav', 'footer']):
                tag.decompose()
                
            # Extrai o texto principal
            texto_principal = self._extrair_texto_principal(soup)
            
            # Lista de estratégias de extração em ordem de preferência
            estrategias = [
                ('IA', lambda: self._extrair_dados_com_ia(texto_principal)),
                ('Padrões', lambda: self._extrair_dados_por_padroes(texto_principal)),
                ('HTML Estruturado', lambda: self._extrair_dados_estruturados(soup)),
                ('Heurística', lambda: self._extrair_dados_heuristicos(texto_principal, soup))
            ]
            
            dados_combinados = {}
            erros = []
            
            # Tenta cada estratégia e combina os resultados
            for nome, estrategia in estrategias:
                try:
                    self.logger.info(f"Tentando estratégia: {nome}")
                    dados = estrategia()
                    if dados:
                        dados_combinados.update(dados)
                        self.logger.info(f"Estratégia {nome} extraiu {len(dados)} campos")
                except Exception as e:
                    self.logger.warning(f"Erro na estratégia {nome}: {str(e)}")
                    erros.append(f"{nome}: {str(e)}")
            
            # Extrai imagens e documentos
            try:
                imagens = self._extrair_imagens(soup, url)
                documentos = self._extrair_documentos(soup, url)
                
                if imagens:
                    dados_combinados['imagens'] = imagens
                if documentos:
                    dados_combinados['documentos'] = documentos
            except Exception as e:
                self.logger.warning(f"Erro ao extrair mídia: {str(e)}")
                erros.append(f"Extração de mídia: {str(e)}")
            
            if not dados_combinados:
                return {
                    'erro': 'Todas as estratégias de extração falharam',
                    'detalhes': erros
                }
            
            # Valida e normaliza os dados combinados
            dados_validados = self._validar_dados(dados_combinados)
            
            # Adiciona metadados
            dados_validados.update({
                'url': url,
                'data_extracao': datetime.now().isoformat(),
                'confiabilidade': self._calcular_confiabilidade(dados_validados),
                'estrategias_usadas': [nome for nome, _ in estrategias if any(campo in dados_validados for campo in dados_combinados)]
            })
            
            return dados_validados
            
        except Exception as e:
            self.logger.error(f"Erro ao extrair dados: {str(e)}")
            return {'erro': str(e)}
            
    def _fazer_requisicao(self, url: str) -> str:
        """Faz requisição HTTP com retry e rotação de user agents"""
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0'
        ]
        
        headers = {
            'User-Agent': random.choice(user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
        max_retries = 3
        retry_delay = 2
        
        for attempt in range(max_retries):
            try:
                response = requests.get(url, headers=headers, timeout=10)
                response.raise_for_status()
                return response.text
            except requests.RequestException as e:
                self.logger.warning(f"Tentativa {attempt + 1} falhou: {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay * (attempt + 1))
                else:
                    raise
                    
    def _extrair_texto_principal(self, soup: BeautifulSoup) -> str:
        """Extrai o texto principal relevante da página"""
        # Remove elementos de navegação e rodapé
        for tag in soup(['nav', 'footer', 'header', 'aside']):
            tag.decompose()
            
        # Identifica o container principal
        main_content = None
        
        # Tenta encontrar por ID/classe comum
        for selector in ['main', '#main', '.main', '#content', '.content', 'article']:
            main_content = soup.select_one(selector)
            if main_content:
                break
                
        # Se não encontrar, usa o body
        if not main_content:
            main_content = soup.body
            
        return main_content.get_text(separator=' ', strip=True)
        
    def _extrair_dados_com_ia(self, texto: str) -> Dict[str, Any]:
        """Extrai dados usando GPT para análise semântica ou padrões quando IA não disponível"""
        try:
            if not texto:
                self.logger.warning("Texto vazio fornecido para análise")
                return {}
                
            self.logger.info("Iniciando extração de dados")
            
            # Se não houver chave da API OpenAI, usa apenas extração por padrões
            if not os.getenv('OPENAI_API_KEY'):
                self.logger.warning("Chave da API OpenAI não configurada. Usando apenas extração por padrões.")
                return self._extrair_dados_por_padroes(texto)
            
            prompt = f"""
            Analise o seguinte texto de um site de leilão e extraia as informações relevantes sobre o imóvel.
            Retorne apenas um objeto JSON com os seguintes campos (se encontrados):
            
            - titulo
            - tipo_imovel
            - endereco
            - area
            - valor_inicial
            - valor_avaliacao
            - data_leilao
            - tipo_leilao
            - processo
            - descricao
            
            Texto: {texto[:4000]}  # Limita o tamanho do texto
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Você é um especialista em extrair dados estruturados de textos sobre leilões de imóveis."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1
            )
            
            try:
                dados = eval(response.choices[0].message.content)
                self.logger.info("Dados extraídos com sucesso usando IA")
                return dados
            except Exception as e:
                self.logger.error(f"Erro ao processar resposta da IA: {str(e)}")
                return self._extrair_dados_por_padroes(texto)
                
        except Exception as e:
            self.logger.error(f"Erro na extração com IA: {str(e)}")
            return self._extrair_dados_por_padroes(texto)
            
    def _extrair_dados_por_padroes(self, texto: str) -> Dict[str, Any]:
        """Extrai dados usando padrões regex"""
        dados = {}
        
        # Extrai valores monetários
        valores = re.findall(self.patterns['valor'], texto)
        if valores:
            # Tenta identificar valor inicial e de avaliação
            if len(valores) >= 2:
                dados['valor_inicial'] = self._normalizar_valor(valores[0])
                dados['valor_avaliacao'] = self._normalizar_valor(valores[1])
            elif len(valores) == 1:
                dados['valor_inicial'] = self._normalizar_valor(valores[0])
                
        # Extrai área
        area_match = re.search(self.patterns['area'], texto)
        if area_match:
            dados['area'] = self._normalizar_area(area_match.group())
            
        # Extrai matrícula
        matricula_match = re.search(self.patterns['matricula'], texto)
        if matricula_match:
            dados['matricula'] = matricula_match.group()
            
        # Extrai processo
        processo_match = re.search(self.patterns['processo'], texto)
        if processo_match:
            dados['processo'] = processo_match.group()
            
        # Extrai data
        data_match = re.search(self.patterns['data'], texto)
        if data_match:
            dados['data_leilao'] = data_match.group()
            
        return dados
        
    def _normalizar_valor(self, valor: str) -> float:
        """Normaliza um valor monetário para float"""
        try:
            # Remove R$, pontos e espaços
            valor_limpo = re.sub(r'[R$\s.]', '', valor.lower())
            
            # Trata sufixos de mil/milhões
            if 'mil' in valor_limpo:
                valor_limpo = valor_limpo.replace('mil', '')
                multiplicador = 1000
            elif 'milhoes' in valor_limpo or 'milhões' in valor_limpo:
                valor_limpo = valor_limpo.replace('milhoes', '').replace('milhões', '')
                multiplicador = 1000000
            else:
                multiplicador = 1
                
            # Substitui vírgula por ponto
            valor_limpo = valor_limpo.replace(',', '.')
            
            # Remove caracteres não numéricos
            valor_limpo = re.sub(r'[^\d.]', '', valor_limpo)
            
            return float(valor_limpo) * multiplicador
        except:
            self.logger.warning(f"Erro ao normalizar valor: {valor}")
            return 0.0
            
    def _normalizar_area(self, area: str) -> float:
        """Normaliza uma área para float"""
        try:
            # Remove unidades e espaços
            area_limpa = re.sub(r'm²|metros quadrados|m2|\s+', '', area.lower())
            
            # Substitui vírgula por ponto
            area_limpa = area_limpa.replace(',', '.')
            
            # Remove caracteres não numéricos
            area_limpa = re.sub(r'[^\d.]', '', area_limpa)
            
            return float(area_limpa)
        except:
            self.logger.warning(f"Erro ao normalizar área: {area}")
            return 0.0
            
    def _validar_dados(self, dados: Dict[str, Any]) -> Dict[str, Any]:
        """Valida e normaliza os dados extraídos"""
        dados_validados = {}
        
        # Validações específicas para cada campo
        if 'titulo' in dados and dados['titulo']:
            dados_validados['titulo'] = str(dados['titulo']).strip()
            
        if 'endereco' in dados and dados['endereco']:
            dados_validados['endereco'] = str(dados['endereco']).strip()
            
        if 'area' in dados and dados['area']:
            try:
                area = float(str(dados['area']).replace(',', '.'))
                if area > 0:
                    dados_validados['area'] = area
            except:
                self.logger.warning(f"Área inválida: {dados['area']}")
                
        if 'valor_inicial' in dados and dados['valor_inicial']:
            try:
                valor = float(str(dados['valor_inicial']).replace(',', '.'))
                if valor > 0:
                    dados_validados['valor_inicial'] = valor
            except:
                self.logger.warning(f"Valor inicial inválido: {dados['valor_inicial']}")
                
        if 'valor_avaliacao' in dados and dados['valor_avaliacao']:
            try:
                valor = float(str(dados['valor_avaliacao']).replace(',', '.'))
                if valor > 0:
                    dados_validados['valor_avaliacao'] = valor
            except:
                self.logger.warning(f"Valor de avaliação inválido: {dados['valor_avaliacao']}")
                
        if 'data_leilao' in dados and dados['data_leilao']:
            try:
                # Tenta diferentes formatos de data
                formatos = ['%d/%m/%Y', '%d-%m-%Y', '%Y-%m-%d',
                           '%d de %B de %Y', '%d %B %Y']
                data_str = str(dados['data_leilao'])
                
                for formato in formatos:
                    try:
                        datetime.strptime(data_str, formato)
                        dados_validados['data_leilao'] = data_str
                        break
                    except:
                        continue
                        
                if 'data_leilao' not in dados_validados:
                    self.logger.warning(f"Data inválida: {data_str}")
            except:
                self.logger.warning(f"Erro ao processar data: {dados['data_leilao']}")
                
        # Campos opcionais
        campos_opcionais = ['tipo_imovel', 'tipo_leilao', 'processo', 'descricao', 'matricula']
        for campo in campos_opcionais:
            if campo in dados and dados[campo]:
                dados_validados[campo] = str(dados[campo]).strip()
                
        return dados_validados
        
    def _calcular_confiabilidade(self, dados: Dict[str, Any]) -> float:
        """Calcula um índice de confiabilidade dos dados extraídos"""
        campos_essenciais = ['titulo', 'endereco', 'valor_inicial', 'data_leilao']
        campos_importantes = ['area', 'valor_avaliacao', 'processo']
        
        pontuacao = 0
        total_campos = len(campos_essenciais) + len(campos_importantes)
        
        # Verifica campos essenciais (peso 2)
        for campo in campos_essenciais:
            if campo in dados and dados[campo]:
                pontuacao += 2
                
        # Verifica campos importantes (peso 1)
        for campo in campos_importantes:
            if campo in dados and dados[campo]:
                pontuacao += 1
                
        # Calcula porcentagem
        max_pontuacao = 2 * len(campos_essenciais) + len(campos_importantes)
        confiabilidade = (pontuacao / max_pontuacao) * 100
        
        return round(confiabilidade, 2)

    def _extrair_dados_estruturados(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extrai dados de elementos HTML estruturados"""
        dados = {}
        
        # Seletores comuns em sites de leilão
        seletores = {
            'titulo': ['h1.titulo', '.titulo-lote', '.titulo-imovel'],
            'endereco': ['.endereco', '.localizacao', '[itemprop="address"]'],
            'area': ['.area', '.metros', '[data-area]'],
            'valor_inicial': ['.valor-inicial', '.lance-inicial', '.preco'],
            'valor_avaliacao': ['.valor-avaliacao', '.avaliacao'],
            'data_leilao': ['.data-leilao', '.data', '[data-leilao]']
        }
        
        for campo, lista_seletores in seletores.items():
            for seletor in lista_seletores:
                elemento = soup.select_one(seletor)
                if elemento:
                    dados[campo] = elemento.get_text(strip=True)
                    break
        
        return dados

    def _extrair_dados_heuristicos(self, texto: str, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extrai dados usando heurísticas e análise contextual avançada"""
        dados = {}
        
        # Divide o texto em parágrafos e normaliza
        paragrafos = [p.strip() for p in texto.split('\n') if p.strip()]
        
        # Dicionário de padrões para identificação
        padroes = {
            'tipo_imovel': [
                'apartamento', 'casa', 'terreno', 'imóvel', 'sala comercial',
                'galpão', 'prédio', 'loja', 'sobrado', 'chácara', 'sítio',
                'fazenda', 'flat', 'kitnet', 'cobertura', 'box'
            ],
            'tipo_leilao': [
                'primeiro leilão', 'segundo leilão', 'leilão único',
                'hasta pública', 'praça única', 'primeira praça', 'segunda praça'
            ],
            'status_leilao': [
                'em andamento', 'encerrado', 'suspenso', 'cancelado',
                'arrematado', 'deserto', 'aguardando', 'próximo'
            ],
            'indicadores_endereco': [
                'rua', 'avenida', 'av.', 'alameda', 'travessa', 'praça',
                'rodovia', 'estrada', 'via', 'largo', 'viela', 'beco',
                'quadra', 'lote', 'condomínio'
            ],
            'indicadores_area': [
                'metros quadrados', 'metros construídos', 'área total',
                'área privativa', 'área útil', 'área construída',
                'área do terreno', 'área comum'
            ]
        }
        
        # Expressões regulares mais específicas
        regex = {
            'inscricao_municipal': r'inscri[çc][ãa]o\s*(?:municipal|imobiliária)?\s*(?:n[°º.]?)?\s*[\d./-]+',
            'matricula': r'matr[íi]cula\s*(?:n[°º.]?)?\s*[\d./-]+\s*(?:do|no|da)?\s*(?:\d+[°º]?)?\s*(?:CRI|RI|Registro de Imóveis)?',
            'contribuinte': r'contribuinte\s*(?:n[°º.]?)?\s*[\d./-]+',
            'coordenadas': r'[-+]?\d{1,3}\.\d+,\s*[-+]?\d{1,3}\.\d+',
            'cep': r'CEP\s*[\d.-]{8,10}',
            'data_formatada': r'\d{1,2}\s+de\s+(?:janeiro|fevereiro|março|abril|maio|junho|julho|agosto|setembro|outubro|novembro|dezembro)\s+de\s+\d{4}',
            'valor_formatado': r'R\$\s*[\d.,]+(?:\s*(?:mil|milh[õo]es|bi|bilh[õo]es))?'
        }
        
        # Análise contextual por parágrafo
        for i, p in enumerate(paragrafos):
            p_lower = p.lower()
            
            # Identifica título combinando tipo de imóvel e localização
            if not dados.get('titulo') and i < 3:  # Normalmente o título está no início
                for tipo in padroes['tipo_imovel']:
                    if tipo in p_lower and len(p) < 200:
                        dados['titulo'] = p
                        dados['tipo_imovel'] = tipo
                        break
            
            # Identifica tipo de leilão e status
            for tipo in padroes['tipo_leilao']:
                if tipo in p_lower:
                    dados['tipo_leilao'] = tipo
                    # Procura status próximo ao tipo
                    for status in padroes['status_leilao']:
                        if status in p_lower:
                            dados['status_leilao'] = status
                            break
            
            # Identifica endereço completo
            if not dados.get('endereco'):
                for ind in padroes['indicadores_endereco']:
                    if ind in p_lower:
                        # Verifica se tem CEP ou cidade/estado junto
                        if re.search(regex['cep'], p) or re.search(r'(?:cidade|município)\s+de\s+[\w\s]+(?:[/-]\s*[A-Z]{2})?', p):
                            dados['endereco'] = p
                            break
            
            # Extrai áreas com contexto
            for ind in padroes['indicadores_area']:
                if ind in p_lower:
                    match = re.search(r'\d+[.,]?\d*\s*(?:m²|metros?(?:\s*quadrados?)?)', p_lower)
                    if match:
                        area_key = 'area_' + ind.replace(' ', '_')
                        dados[area_key] = self._normalizar_area(match.group())
            
            # Extrai valores monetários com contexto
            valores_match = re.finditer(regex['valor_formatado'], p)
            for match in valores_match:
                valor = match.group()
                # Identifica o contexto do valor
                contexto_anterior = p_lower[max(0, match.start() - 50):match.start()]
                if 'avaliação' in contexto_anterior or 'avaliado' in contexto_anterior:
                    dados['valor_avaliacao'] = self._normalizar_valor(valor)
                elif 'inicial' in contexto_anterior or 'mínimo' in contexto_anterior:
                    dados['valor_inicial'] = self._normalizar_valor(valor)
                elif not dados.get('valor_inicial'):  # Valor sem contexto específico
                    dados['valor_inicial'] = self._normalizar_valor(valor)
            
            # Extrai datas formatadas
            datas_match = re.finditer(regex['data_formatada'], p)
            for match in datas_match:
                data = match.group()
                contexto_anterior = p_lower[max(0, match.start() - 30):match.start()]
                if 'leilão' in contexto_anterior or 'praça' in contexto_anterior:
                    dados['data_leilao'] = data
            
            # Extrai informações de registro
            for campo, padrao in regex.items():
                if campo in ['inscricao_municipal', 'matricula', 'contribuinte']:
                    match = re.search(padrao, p_lower)
                    if match and campo not in dados:
                        dados[campo] = match.group()
        
        # Pós-processamento para campos específicos
        if 'area' in dados:
            area_total = dados['area']
            # Se houver múltiplas áreas, usa a maior como área total
            areas = [v for k, v in dados.items() if k.startswith('area_') and isinstance(v, (int, float))]
            if areas:
                area_total = max(areas)
            dados['area'] = area_total
        
        return dados

    def _processar_imagem_ocr(self, url_img: str, contexto: str = None) -> Dict[str, Any]:
        """Processa uma imagem com OCR e retorna o texto e metadados"""
        try:
            # Verifica cache
            if url_img in self._ocr_cache:
                self.logger.info(f"Usando resultado em cache para {url_img}")
                return self._ocr_cache[url_img]
            
            # Baixa a imagem
            response = requests.get(url_img, timeout=10)
            response.raise_for_status()
            
            # Converte para formato PIL
            img = Image.open(BytesIO(response.content))
            
            # Pré-processamento da imagem
            img_array = np.array(img)
            
            # Converte para escala de cinza se necessário
            if len(img_array.shape) == 3:
                img_gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            else:
                img_gray = img_array
            
            # Aplica threshold adaptativo
            img_thresh = cv2.adaptiveThreshold(
                img_gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY, 11, 2
            )
            
            # Reduz ruído
            img_denoised = cv2.fastNlMeansDenoising(img_thresh)
            
            # Converte de volta para PIL
            img_processed = Image.fromarray(img_denoised)
            
            # Configura OCR para português
            config = '--oem 3 --psm 6 -l por'
            
            # Extrai texto
            texto = pytesseract.image_to_string(img_processed, config=config)
            
            # Extrai dados estruturados
            dados = pytesseract.image_to_data(img_processed, config=config, output_type=pytesseract.Output.DICT)
            
            # Analisa o texto extraído com base no contexto
            texto_analisado = self._analisar_texto_ocr(texto, contexto)
            
            resultado = {
                'texto': texto,
                'dados_estruturados': texto_analisado,
                'confianca_media': np.mean([float(conf) for conf in dados['conf'] if conf != '-1']),
                'palavras_detectadas': len([word for word in dados['text'] if word.strip()]),
                'contexto': contexto
            }
            
            # Armazena no cache
            self._ocr_cache[url_img] = resultado
            
            return resultado
            
        except Exception as e:
            self.logger.error(f"Erro no processamento OCR da imagem {url_img}: {str(e)}")
            return {'erro': str(e)}

    def _analisar_texto_ocr(self, texto: str, contexto: str = None) -> Dict[str, Any]:
        """Analisa o texto extraído por OCR com base no contexto"""
        dados = {}
        
        if not texto:
            return dados
            
        texto_lower = texto.lower()
        
        # Análise baseada no contexto
        if contexto == 'planta':
            # Procura por informações de área
            areas = re.findall(r'\d+[.,]?\d*\s*(?:m²|metros?(?:\s*quadrados?)?)', texto_lower)
            if areas:
                dados['areas_detectadas'] = [self._normalizar_area(area) for area in areas]
                
            # Procura por informações de cômodos
            comodos = re.findall(r'\d+\s*(?:quarto|dormitório|suíte|banheiro|sala|cozinha|vaga)', texto_lower)
            if comodos:
                dados['comodos'] = comodos
                
        elif contexto == 'documento':
            # Procura por números de registro/matrícula
            matriculas = re.findall(r'matrícula\s*(?:n[°º.]?)?\s*[\d./-]+', texto_lower)
            if matriculas:
                dados['matriculas'] = matriculas
                
            # Procura por CPF/CNPJ
            documentos = re.findall(r'\d{2}[\.]?\d{3}[\.]?\d{3}[\/]?\d{4}[-]?\d{2}|\d{3}[\.]?\d{3}[\.]?\d{3}[-]?\d{2}', texto)
            if documentos:
                dados['documentos'] = documentos
                
        elif contexto == 'mapa':
            # Procura por coordenadas
            coordenadas = re.findall(r'[-+]?\d{1,3}\.\d+,\s*[-+]?\d{1,3}\.\d+', texto)
            if coordenadas:
                dados['coordenadas'] = coordenadas
                
            # Procura por CEP
            ceps = re.findall(r'\d{5}[-]?\d{3}', texto)
            if ceps:
                dados['ceps'] = ceps
                
        # Análise geral
        # Procura por valores monetários
        valores = re.findall(r'R\$\s*[\d.,]+(?:\s*(?:mil|milh[õo]es|bi|bilh[õo]es))?', texto)
        if valores:
            dados['valores'] = [self._normalizar_valor(valor) for valor in valores]
            
        # Procura por datas
        datas = re.findall(r'\d{1,2}[/-]\d{1,2}[/-]\d{4}|\d{1,2}\s+(?:de\s+)?(?:janeiro|fevereiro|março|abril|maio|junho|julho|agosto|setembro|outubro|novembro|dezembro)\s+(?:de\s+)?\d{4}', texto_lower)
        if datas:
            dados['datas'] = datas
            
        return dados

    def _extrair_imagens(self, soup: BeautifulSoup, url_base: str) -> List[Dict[str, Any]]:
        """Extrai imagens relevantes da página com suporte a OCR"""
        imagens = []
        
        # Função para resolver URLs relativas
        def resolver_url(url_relativa: str) -> str:
            if url_relativa.startswith(('http://', 'https://')):
                return url_relativa
            return requests.compat.urljoin(url_base, url_relativa)
        
        # Função para validar extensão de arquivo
        def extensao_valida(url: str) -> bool:
            ext = os.path.splitext(url.split('?')[0].lower())[1]
            return ext in self.tipos_imagem
            
        # Busca imagens em diferentes contextos
        seletores_imagem = {
            'galeria': ['div.galeria img', '.fotos img', '.slider img'],
            'principal': ['.imagem-principal img', '.foto-destaque img'],
            'planta': ['.planta img', '.blueprint img'],
            'mapa': ['.mapa img', '.localizacao img'],
            'documento': ['.documento img', '.certidao img', '.matricula img']
        }
        
        for contexto, seletores in seletores_imagem.items():
            for seletor in seletores:
                for img in soup.select(seletor):
                    try:
                        # Tenta diferentes atributos de URL
                        url_img = img.get('data-src') or img.get('src')
                        if not url_img:
                            continue
                            
                        url_img = resolver_url(url_img)
                        
                        if not extensao_valida(url_img):
                            continue
                            
                        # Extrai metadados da imagem
                        metadados = {
                            'url': url_img,
                            'tipo': contexto,
                            'alt': img.get('alt', ''),
                            'titulo': img.get('title', ''),
                            'largura': img.get('width', ''),
                            'altura': img.get('height', ''),
                            'data_modificacao': img.get('data-modified', '')
                        }
                        
                        # Processa OCR se necessário
                        if contexto in ['planta', 'documento', 'mapa']:
                            resultado_ocr = self._processar_imagem_ocr(url_img, contexto)
                            if 'erro' not in resultado_ocr:
                                metadados['ocr'] = resultado_ocr
                        
                        # Remove metadados vazios
                        metadados = {k: v for k, v in metadados.items() if v}
                        
                        imagens.append(metadados)
                        
                    except Exception as e:
                        self.logger.warning(f"Erro ao processar imagem: {str(e)}")
                        continue
        
        return imagens

    def _extrair_documentos(self, soup: BeautifulSoup, url_base: str) -> List[Dict[str, Any]]:
        """Extrai documentos anexos da página"""
        documentos = []
        
        def resolver_url(url_relativa: str) -> str:
            if url_relativa.startswith(('http://', 'https://')):
                return url_relativa
            return requests.compat.urljoin(url_base, url_relativa)
        
        def extensao_valida(url: str) -> bool:
            ext = os.path.splitext(url.split('?')[0].lower())[1]
            return ext in self.tipos_documento
            
        # Busca links para documentos
        seletores_documento = {
            'edital': ['a[href*="edital"]', '.documentos a[href$=".pdf"]'],
            'matricula': ['a[href*="matricula"]', 'a[href*="certidao"]'],
            'laudo': ['a[href*="laudo"]', 'a[href*="avaliacao"]'],
            'processo': ['a[href*="processo"]', 'a[href*="autos"]']
        }
        
        for tipo, seletores in seletores_documento.items():
            for seletor in seletores:
                for link in soup.select(seletor):
                    try:
                        url_doc = link.get('href')
                        if not url_doc:
                            continue
                            
                        url_doc = resolver_url(url_doc)
                        
                        if not extensao_valida(url_doc):
                            continue
                            
                        # Extrai metadados do documento
                        metadados = {
                            'url': url_doc,
                            'tipo': tipo,
                            'titulo': link.get_text(strip=True),
                            'extensao': os.path.splitext(url_doc.split('?')[0])[1],
                            'data_modificacao': link.get('data-modified', '')
                        }
                        
                        # Tenta extrair tamanho do arquivo se disponível
                        tamanho = link.get('data-size') or link.get('size')
                        if tamanho:
                            metadados['tamanho'] = tamanho
                            
                        # Remove metadados vazios
                        metadados = {k: v for k, v in metadados.items() if v}
                        
                        documentos.append(metadados)
                        
                    except Exception as e:
                        self.logger.warning(f"Erro ao processar documento: {str(e)}")
                        continue
        
        return documentos 