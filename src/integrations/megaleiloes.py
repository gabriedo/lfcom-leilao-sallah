from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
import json

def extract_data(url):
    try:
        # Configurar o Chrome em modo headless
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
        
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(url)
        
        # Aguardar o carregamento da página
        time.sleep(5)
        
        # Extrair dados
        data = {
            'titulo': '',
            'endereco': '',
            'descricao': '',
            'valor': '',
            'edital': '',
            'data_leilao': '',
            'tipo_imovel': '',
            'area': '',
            'quartos': '',
            'banheiros': '',
            'vagas': ''
        }
        
        try:
            # Título
            titulo = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "h1.property-title"))
            )
            data['titulo'] = titulo.text.strip()
            
            # Endereço
            endereco = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.property-address"))
            )
            data['endereco'] = endereco.text.strip()
            
            # Descrição
            descricao = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.property-description"))
            )
            data['descricao'] = descricao.text.strip()
            
            # Valor
            valor = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.property-values"))
            )
            data['valor'] = valor.text.strip()
            
            # Características
            caracteristicas = driver.find_elements(By.CSS_SELECTOR, "div.property-features li")
            for item in caracteristicas:
                texto = item.text.lower()
                if 'área' in texto:
                    data['area'] = texto.split(':')[-1].strip()
                elif 'quartos' in texto:
                    data['quartos'] = texto.split(':')[-1].strip()
                elif 'banheiros' in texto:
                    data['banheiros'] = texto.split(':')[-1].strip()
                elif 'vagas' in texto:
                    data['vagas'] = texto.split(':')[-1].strip()
            
            # Edital e data do leilão
            info_adicional = driver.find_elements(By.CSS_SELECTOR, "div.property-additional-info li")
            for item in info_adicional:
                texto = item.text.lower()
                if 'edital' in texto:
                    data['edital'] = texto.split(':')[-1].strip()
                elif 'data' in texto and 'leilão' in texto:
                    data['data_leilao'] = texto.split(':')[-1].strip()
            
        except TimeoutException:
            print("Timeout ao esperar elementos da página")
        except Exception as e:
            print(f"Erro ao extrair dados: {str(e)}")
        
        driver.quit()
        return data
        
    except Exception as e:
        print(f"Erro ao acessar a página: {str(e)}")
        return None

if __name__ == "__main__":
    url = "https://www.megaleiloes.com.br/imoveis/apartamentos/sp/birigui/direitos-sobre-apartamento-54-m2-residencial-manuela-birigui-sp-j108846"
    data = extract_data(url)
    print(json.dumps(data, indent=2, ensure_ascii=False)) 