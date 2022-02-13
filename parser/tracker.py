from bs4 import BeautifulSoup
from selenium import webdriver
import requests, random, re

USER_AGENT_LIST = [
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.1 Safari/605.1.15',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:77.0) Gecko/20100101 Firefox/77.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:77.0) Gecko/20100101 Firefox/77.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36'
]

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

    def check_connections(self):
        remove_urls = []
        for url in self.urls:
            try:
                connection_code = requests.get(url, headers=self.client_headers).status_code
                if connection_code != 200:
                    print('Status code %s: %d' % (url, connection_code))
                    remove_urls.append(url)
            except requests.exceptions.ConnectionError:
                remove_urls.append(url)

        for url in remove_urls:
            self.urls.remove(url)

        return 0

    def get_products_info(self):
        if self.check_connections() < 0:
            return -1

        for url in self.urls:
            self.products.append(self.get_product_name_price(url))

        return self.products

    def get_product_name_price(self, url):
        site_content = requests.get(url, headers=self.client_headers).text
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

class DNS(ProductInfo):
    def __init__(self, url=None, shop=None):
        super().__init__(url, shop)
        options = webdriver.FirefoxOptions()
        options.headless = True
        self.browser = webdriver.Firefox(executable_path='geckodriver.exe', options=options)

    def get_product_name_price(self, url):
        class_product_price = 'product-buy__price'
        class_product_name = 'product-card-top__title'
        self.browser.get(url)
        site_content = self.browser.page_source
        soup = BeautifulSoup(site_content, 'lxml')
        price = soup.find_all('div', class_=class_product_price)
        name = soup.find_all('h1', class_=class_product_name)

        if not price or not name:
            #print('Product not found')
            return (None, None)
        else:
            price = price[0].text[:-1].strip()
            name = name[0].text.strip()

        return (name, price)

    def get_products_info(self):
        for url in self.urls:
            name, price = self.get_product_name_price(url)

            if name and price:
                self.products.append((name, price))

    def close(self):
        self.browser.quit()
