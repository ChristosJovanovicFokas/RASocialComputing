from bs4 import BeautifulSoup

path = r'data/html/fd52e9e75ad1221a9243a01fbc33f3e8.html'

with open(path, 'r', encoding='utf-8') as f:
    html = f.read()

soup = BeautifulSoup(html, "html.parser")

print(soup.a.prettify())
#links = main.find('tag', 'a')

#for link in links:
    #print(links)