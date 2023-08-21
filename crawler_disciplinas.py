import json
import utils
from urllib.request import urlopen
from urllib.error import HTTPError
from bs4 import BeautifulSoup


def make_soup(url):
    html = urlopen(url).read()

    return BeautifulSoup(html, features="html.parser")


def get_name(soup):
    name = soup.find('div', {'class': 'pessoa-nome'}) # Tenta encontrar o nome na tag ideal 

    if not name:
        name = soup.find('div', {'class': 'documentDescription'}) # Usa o subtitulo se nao encontrar 

    if not name:
        name = soup.find('h1', {'class': 'documentFirstHeading'}) # Usa o titulo como ultima opcao

    name = name.text if name else None

    return name


def get_role(soup):
    role = soup.find('h1', {'class': 'documentFirstHeading'})
    role = role.text if role else None

    return role


def get_appointments(soup):
    appointments = []
    events = soup.find('ul', {'class': 'list-compromissos'}).findAll('li')

    if soup.find('li', {'class': 'sem-compromisso'}):
        return []

    for event in events:
        event_name = event.find('h4', {'class': 'compromisso-titulo'})
        event_name = event_name.text if event_name else 'NA'

        datetime_event = event.find('time', {'class': 'compromisso-inicio'})
        datetime_event = datetime_event.text if datetime_event else 'NA'
        datetime_event = utils.convert_time(datetime_event)

        event_place = event.find('div', {'class': 'compromisso-local'})
        event_place = event_place.text if event_place else 'NA'

        appointment = {
            'Hora inicio': datetime_event,
            'Nome do evento': event_name,
            'Local do evento': event_place,
        }
        appointments.append(appointment)

    return appointments


def get_authority(link):
    try:
        soup = make_soup(link)
    except HTTPError as error404:
        print('error 404:', link)
        return {}

    name = get_name(soup)
    if not name:
        return {}

    role = get_role(soup)
    role = utils.clean_role(role, name)
    name = utils.clean_name(name, role)

    appointments = get_appointments(soup)
    authority = {
        "nome": name,
        "cargo": role,
        "eventos": appointments,
    }

    return authority


def get_authority_links(link):
    soup = make_soup(link)
    links = []
    authorities = soup.findAll('a', {'class': 'internal-link'})

    for authority in authorities:
        links.append(authority['href'])

    return links


def get_role_links(url):
    soup = make_soup(url)
    p_tags = soup.findAll('p')
    role_links = []

    for p_tag in p_tags:
        role_link = [(link['href']) for link in p_tag.findAll('a')]
        role_links.append(role_link)

    return utils.flatten(role_links)


if __name__ == '__main__':

    BASE_URL = 'https://sig.unb.br/sigaa/public/curso/lista.jsf?nivel=G&aba=p-ensino'

    authorities_role = get_role_links(BASE_URL)
    print('bora craalho hahahahahahhahahahahahahhahah')
    authorities = []
    authorities_agenda = []

    for link in authorities_role:
        authorities.append(get_authority_links(link))

    authorities = utils.flatten(authorities)

    for authority in authorities:
        agenda = get_authority(authority)
        if agenda:
            authorities_agenda.append(agenda)

    with open('authorities_agenda.json', 'w') as file:
        json.dump(authorities_agenda, file)
