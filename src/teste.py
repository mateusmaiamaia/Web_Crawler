import json
import utils
from urllib import urlopen
from urllib.error import HTTPError
from bs4 import BeautifulSoup


def make_soup(url):
    html = urlopen(url).read()

    return BeautifulSoup(html, features="html.parser")


def get_role_links(url):
    soup = make_soup(url)
    p_tags = soup.find('table')
    print(p_tags)
    role_links = []

    for p_tag in p_tags:
        role_link = [(link['href']) for link in p_tag.findAll('a')]
        role_links.append(role_link)

    return utils.flatten(role_links)


if __name__ == '__main__':

    BASE_URL = 'https://sig.unb.br/sigaa/public/curso/lista.jsf?nivel=G&aba=p-ensino'

    authorities_role = get_role_links(BASE_URL)
   
    authorities = []
    authorities_agenda = []

    with open('authorities_agenda.json', 'w') as file:
        json.dump(authorities_agenda, file)
