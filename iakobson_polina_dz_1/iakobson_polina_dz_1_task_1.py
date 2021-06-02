# Задание 1
# Источник: https://5ka.ru/special_offers/
# Задача организовать сбор данных,
# необходимо иметь метод сохранения данных в .json файлы
# результат: Данные скачиваются с источника, при вызове метода/функции сохранения в файл скачанные данные
# сохраняются в Json файлы, для каждой категории товаров должен быть создан отдельный файл
# и содержать товары исключительно соответсвующие данной категории.
# пример структуры данных для файла:
# нейминг ключей можно делать отличным от примера
#
# {
# "name": "имя категории",
# "code": "Код соответсвующий категории (используется в запросах)",
# "products": [{PRODUCT}, {PRODUCT}........] # список словарей товаров соответсвующих данной категории
# }

# Перенесла код парсера с урока:

from pathlib import Path
import requests
import time
import json

# url = 'https://5ka.ru/special_offers/'
#
# headers = {'User-Agent': 'Local User'}
# response = requests.get(url, headers=headers)
#
# test_file = pathlib.Path(__file__).parent.joinpath('test_file.html')
# test_file.write_bytes(response.content)

class Parser5ka:
    headers = {
        'User-Agent': 'Local User'
    }
    def __init__(self, start_url: str, save_dir: Path):
        self.start_url = start_url
        self.save_dir = save_dir

    def get_response(self, url: str) -> requests.Response:
        while True:
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                return response
            time.sleep(0.2)


    def run(self):
        for product in self.parse(self.start_url):
            file_name = f"{product['id']}.json"
            file_path = self.save_dir.joinpath(file_name)
            self.save(product, file_path)

    def parse(self, url):
        while url:
            response = self.get_response(url)
            data = response.json()
            url = data['next']
            for product in data['results']:
                yield product


    def save(self, data:dict, file_path = Path):
        file_path.write_text(json.dumps(data))

def get_dir_path(dir_name: str) -> Path:
    dir_path = Path(__file__).parent.joinpath(dir_name)
    if not dir_path.exists():
        dir_path.mkdir()
    return dir_path

if __name__ == '__main__':
    url = 'https://5ka.ru/api/v2/special_offers/recommended/'
    save_dir = get_dir_path('products')
    parser = Parser5ka(url, save_dir)
    parser.run()

#------------------------------------
# Парсер по категориям

class CategoriesParser(Parser5ka):
    def __init__(self, categories_url, *args):
        self.categories_url = categories_url
        super().__init__(*args)

    def get_categories(self):
        response = self.get_response(self.categories_url)
        data = response.json()
        return data

    def run(self):
        for category in self.get_categories():
            category['products'] = []
            params = f"?categories={category['parent_group_code']}"
            url = f'{self.start_url}{params}'

            category['products'].extend(list(self.parse(url)))
            file_name = f"{category['parent_group_code']}.json"
            category_path = self.save_dir.joinpath(file_name)
            self.save(category, category_path)

def get_dir_path(dir_name: str) -> Path:
    dir_path = Path(__file__).parent.joinpath(dir_name)
    if not dir_path.exists():
        dir_path.mkdir()
    return dir_path

if __name__ == '__main__':
    url = 'https://5ka.ru/api/v2/special_offers/recommended/'
    save_dir = get_dir_path('products')
    parser = Parser5ka(url, save_dir)
    parser.run()
    category_url = 'https://5ka.ru/api/v2/categories/'
    product_path = get_dir_path('products')
    parser = Parser5ka(url, product_path)
    category_parser = CategoriesParser(category_url, url, get_dir_path('category_products'))
    category_parser.run()