import requests
from bs4 import BeautifulSoup


quote_page = 'https://finance.google.com/finance?q='

stock_index = "NYSE:JPM"

page =requests.get(quote_page + stock_index)

soup = BeautifulSoup(page.content, 'html.parser')

name_box = soup.find('div', attrs={'id': 'price-panel'})
name = name_box.text.strip()

#price_box = soup.find('div', attrs={'class': 'price'})
#price = price_box.text.strip()

print(name)
#print(price)