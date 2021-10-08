import json
from datetime import datetime
from urllib.request import urlopen
from bs4 import BeautifulSoup

BASE_URL = 'https://www.gov.br/ana/pt-br/acesso-a-informacao/agenda-de-autoridades'


def make_soup(url):
    html = urlopen(url).read()
    return BeautifulSoup(html)


def flatten(list):
    flat_list = []
    for sublist in list:
        for item in sublist:
            flat_list.append(item)
    return flat_list


def get_nome(soup):
    nome = soup.find('div', {'class': 'pessoa-nome'})
    if not nome:
        nome = soup.find('div', {'class': 'documentDescription'})
    if not nome:
        nome = soup.find('h1', {'class': 'documentFirstHeading'})
    nome = nome.text if nome else None
    return nome


def get_cargo(soup):
    cargo = soup.find('h1', {'class': 'documentFirstHeading'})
    cargo = cargo.text if cargo else None
    return cargo


def converte_tempo(tempo):
    if tempo == 'NA':
        return tempo
    hora, minuto = tempo.split('h')
    data_ISO = datetime.now().replace(
        hour=int(hora), minute=int(minuto), microsecond=0).isoformat()
    return data_ISO


def get_evento(soup):
    compromissos = []
    eventos = soup.find('ul', {'class': 'list-compromissos'}).findAll('li')
    if soup.find('li', {'class': 'sem-compromisso'}):
        return []
    for evento in eventos:
        nome_evento = evento.find('h4', {'class': 'compromisso-titulo'})
        nome_evento = nome_evento.text if nome_evento else 'NA'

        data_hora_evento = evento.find('time', {'class': 'compromisso-inicio'})
        data_hora_evento = data_hora_evento.text if data_hora_evento else 'NA'
        data_hora_evento = converte_tempo(data_hora_evento)

        local_evento = evento.find('div', {'class': 'compromisso-local'})
        local_evento = local_evento.text if local_evento else 'NA'

        compromisso = {
            'Hora inicio': data_hora_evento,
            'Nome do evento': nome_evento,
            'Local do evento': local_evento,
        }
        compromissos.append(compromisso)
    return compromissos


def get_autoridade_info(link):
    try:
        soup = make_soup(link)
    # tem que pegar a exceção certa 404
    except Exception:
        return {}

    nome_autoridade = get_nome(soup)
    if not nome_autoridade:
        return {}

    cargo_autoridade = get_cargo(soup)
    # limpando nomes e cargos de autoridade 

    if nome_autoridade in cargo_autoridade:
        cargo_autoridade = cargo_autoridade.replace(nome_autoridade, '')
    if cargo_autoridade in nome_autoridade:
        nome_autoridade = nome_autoridade.replace(
            '(' + cargo_autoridade + ')', '')

    compromissos = get_evento(soup)
    pessoa_info = {
        "nome": nome_autoridade,
        "cargo": cargo_autoridade,
        "eventos": compromissos,
    }
    return pessoa_info


def get_autoridade_link(link):
    soup = make_soup(link)
    aux = []
    try:
        link_autoridades = soup.findAll('a', {'class': 'internal-link'})
        for elem_a in link_autoridades:
            aux.append(elem_a['href'])
    except TypeError as error:
        print(error)
    return aux


def get_cargos_links(url):
    soup = make_soup(url)
    row = soup.findAll('p')
    list_links = []
    for elem in row:
        cargos_links = [(link['href']) for link in elem.findAll('a')]
        list_links.append(cargos_links)
    return flatten(list_links)


if __name__ == '__main__':
    autoridades_cargos = (BASE_URL)
    autoridades_cargos = get_cargos_links(autoridades_cargos)
    autoridades = []
    pessoas = []
    for link in autoridades_cargos:
        autoridades.append(get_autoridade_link(link))
    autoridades = flatten(autoridades)
    for autoridade in autoridades:
        pessoa = get_autoridade_info(autoridade)
        # se pessoa for um dicionário vazio ele não sera adicionado
        # no resultado final
        if pessoa:
            pessoas.append(pessoa)

    with open('pessoas.json', 'w') as file:
        json.dump(pessoas, file)
