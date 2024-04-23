from flask import Flask, jsonify, render_template
from flask_cors import CORS
import requests
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
import re
from GoogleNews import GoogleNews

app = Flask(__name__)
CORS(app)

allowed_media = [
    "Jovem Pan", "SBT", "Jornal Correio", "Valor Econômico", "Band Jornalismo",
    "Terra", "Brasil 247", "CNN Brasil", "O Globo", "Estadão", "Poder360",
    "Portal iG", "CartaCapital", "Crusoé", "Metrópoles", "G1", "O Antagonista",
    "Jornal de Brasília", "Hora do Povo", "Gazeta de S. Paulo", "UOL", "VEJA",
    "Gazeta do Povo", "Revista Oeste"
]

def extrair_horas(texto):
    if 'hora' in texto:
        match = re.search(r'(\d+)\s+hora', texto)
        if match:
            return int(match.group(1))
    elif 'ontem' in texto:
        return 24  # Considerar 'ontem' como 24 horas atrás
    elif 'dias' in texto:
        match = re.search(r'(\d+)\s+dia', texto)
        if match:
            return int(match.group(1)) * 24
    return float('inf')  # Para texto que não corresponde a nenhum padrão

@app.route("/") 
def hello():     
    return render_template('index.html')
                           

@app.route('/noticias')
def get_noticias():
    noticias = {
        "camara": [],
        "senado": [],
        "google_news": []
    }
    
    
    # Notícias da Câmara
    url_camara = 'https://www.camara.leg.br/noticias/rss/dinamico/SEGURANCA'
    response = requests.get(url_camara)
    if response.status_code == 200:
        root = ET.fromstring(response.content)
        for item in root.findall('./channel/item'):
            title = item.find('title').text
            link = item.find('link').text
            noticias["camara"].append({"titulo": title, "link": link})

    # Notícias do Senado
    base_url = 'https://www12.senado.leg.br'
    path = '/noticias/tags/Seguran%C3%A7a%20P%C3%BAblica'
    response = requests.get(base_url + path)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        texto_materia = soup.find('div', id='textoMateria')
        if texto_materia:
            noticias_links = texto_materia.find_all('a')
            for link in noticias_links:
                titulo = link.text.strip()
                if titulo == '«':
                    break
                href = link.get('href')
                link_completo = href if href.startswith('http') else base_url + href
                noticias["senado"].append({"titulo": titulo, "link": link_completo})

    # Notícias do Google News
    googlenews = GoogleNews(lang='pt-BR', region='BR', period='1d')
    googlenews.get_news('seguranca publica')
    results_gnews = googlenews.results()

    def extrair_horas(texto):
        match = re.search(r'(\d+)\s+hora', texto)
        if match:
            return int(match.group(1))
        return 0

    dados_ordenados = sorted(results_gnews, key=lambda x: extrair_horas(x['date']))
    for item in dados_ordenados:
        media = item['media'] 
        if media in allowed_media:                       
            date = item['date']       
            title =  item['title']
            link = 'https://' + item['link']
            noticias["google_news"].append({"titulo": title, "link": link, "midia": media, "data": date})

    return jsonify(noticias)

if __name__ == '__main__':
    app.run(debug=True)
