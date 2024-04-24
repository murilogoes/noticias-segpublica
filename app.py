from flask import Flask, jsonify, render_template
from flask_cors import CORS
import requests
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
from datetime import datetime
import pytz

app = Flask(__name__)
CORS(app)

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





    # Suponha que você fez uma requisição GET para a URL
    response = requests.get("https://news.google.com/rss/search?hl=pt-BR&gl=BR&ceid=BR%3Apt-419&oc=11&q=policia%20militar%20when%3A1d")
    xml_content = response.text

    # Parse do conteúdo XML
    root = ET.fromstring(xml_content)

    news_items = []

    for item in root.findall('.//item'):
        title = item.find('title').text
        link = item.find('link').text
        pub_date = item.find('pubDate').text
        data_obj = datetime.strptime(pub_date, '%a, %d %b %Y %H:%M:%S GMT').replace(tzinfo=pytz.utc)

        # Definir o fuso horário de Brasília (UTC-3)
        fuso_brasilia = pytz.timezone('America/Sao_Paulo')

        # Converter para o fuso horário de Brasília
        data_brasilia = data_obj.astimezone(fuso_brasilia)

        # Formatar para o estilo brasileiro
        data_formatada = data_brasilia.strftime('%d/%m/%Y %H:%M:%S')
        source = item.find('source').text

        news_items.append({
            'title': title,
            'link': link,
            'pub_date': data_formatada,
            'source': source
        })

    # Ordenar notícias pela data mais recente
    news_items.sort(key=lambda x: x['pub_date'], reverse=True)
    
    # Converter string para objeto datetime com GMT



    # Dicionário para armazenar as notícias
    #noticias = {"google_news": []}

    # Adicionar ao dicionário
    for item in news_items:
        media = item['source']
        date = item['pub_date']
        title = item['title']
        link = item['link']
        noticias["google_news"].append({"titulo": title, "link": link, "midia": media, "data": date})

    # Mostrar o resultado
    #print(noticias)

    return jsonify(noticias)

if __name__ == '__main__':
    app.run(debug=True)
