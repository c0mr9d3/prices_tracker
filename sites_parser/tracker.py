from bs4 import BeautifulSoup
import requests, random, re

USER_AGENT_LIST = (
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.1 Safari/605.1.15',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:77.0) Gecko/20100101 Firefox/77.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:77.0) Gecko/20100101 Firefox/77.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36'
)
SUPPORTED_SITES = ('ozon.ru', 'citilink.ru')

class ProductInfo:
    def __init__(self, url=None, shop=None):
        if not url:
            self.urls = []
        else:
            self.urls = [url]

        self.products = []
        self.shop = shop

    def add_url(self, url):
        self.urls.append(url)

    def clear_urls_list(self):
        del self.urls
        self.urls = []

class Citilink(ProductInfo):
    class_product_price = ('ProductHeader__price-default_current-price js--ProductHeader__price-default_current-price',)
    class_product_name = 'Heading Heading_level_1 ProductHeader__title'
    client_headers = {
        'User-Agent': random.choice(USER_AGENT_LIST)
    }

    def get_products_info(self):
        for url in self.urls:
            try:
                connection = requests.get(url, headers=self.client_headers)
                if connection.status_code != 200:
                    print('Status code %s: %d' % (url, connection.status_code))
                    continue

                self.products.append(self.get_product_name_price(connection))

            except requests.exceptions.ConnectionError:
                continue

        return self.products

    def get_product_name_price(self, connection):
        site_content = connection.text
        soup = BeautifulSoup(site_content, 'lxml')
        price = ''

        for class_name in self.class_product_price:
            try:
                price = soup.find_all('span', class_=class_name)[0].text.strip()
                price = ''.join(re.findall('\d+', price))
                break
            except IndexError:
                continue

        if not price:
            price = 'Price not found'

        try:
            name = soup.find_all('h1', class_=self.class_product_name)[0].text.strip()
        except IndexError:
            name = 'Error'

        return (name, price)

class Ozon(Citilink):
    class_product_price = ('rj7 r7j', 'rj7 jr8')
    class_product_name = 's9j'
