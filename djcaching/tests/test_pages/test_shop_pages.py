from bs4 import BeautifulSoup
from django.contrib.auth.models import User
from django.db.models import F
from django.test import TestCase
from django.urls import resolve
from app_shops.views import MainPageView, ShopPageView, goods_page_view
from app_shops.models import ShopModel, GoodsModel, GoodsCategoryModel, RatingModel
from app_users.models import UserProfile


class TestMainPage(TestCase):

    user = None

    @classmethod
    def setUpTestData(cls):
        user_data = {'username': 'user_1',
                     'password': "glavryiba"}
        TestMainPage.user = User.objects.create(**user_data)
        user_profile_data = {'user': TestMainPage.user,
                             'first_name': 'Ivan',
                             'surname': 'Ivanov'}
        UserProfile.objects.create(**user_profile_data)
        shop_1_data = {'name': 'very_good_shop',
                       'short_description': "We got all the things!",
                       'full_description': 'Really good choice. Take a look!'}
        ShopModel.objects.create(**shop_1_data)
        rating = {'average': 4.32}
        rating = RatingModel.objects.create(**rating)
        shop_2_data = {'name': 'good_shop',
                       'short_description': "Best prices!",
                       'full_description': 'We have great amount of goods and great prices for our customers!',
                       'rating': rating}
        ShopModel.objects.create(**shop_2_data)

    def test_correct_url(self):
        found = self.client.get('/')
        self.assertEqual(found.status_code, 200)

    def test_correct_view(self):
        found = resolve('/')
        self.assertEqual(found.func.__name__, MainPageView.as_view().__name__)

    def test_correct_template(self):
        found = self.client.get('/')
        self.assertTemplateUsed(found, 'app_shops/main_page.html')

    def test_greeting_anonimus_user(self):
        found = self.client.get('/')
        anonimus_greeting = '''<p>Чтобы совершать покупки, необходимо пройти <a href='login'>аутентификацию</a> или
    <a href='registration'>зарегистрироваться</a></p>'''
        self.assertIn(anonimus_greeting, found.content.decode())

    def test_greeting_authenticated_user(self):
        self.client.force_login(User.objects.get(username='user_1'))
        found = self.client.get('/')
        authenticated_greeting =  '<p>Ваш профиль, <a href="user_profile/user_1">Ivan Ivanov</a></p>'
        self.assertIn(authenticated_greeting, found.content.decode())

    def test_shops_list(self):
        found = self.client.get('/')
        html = found.content.decode('utf-8')
        shop_name = '''<p><a href="/shops/very_good_shop">very_good_shop</a></p>'''
        shop_desc_short = '''<p>We got all the things!</p>'''
        shop_desc_full = '''Really good choice. Take a look!'''
        rating = """<p>У этого магазина ещё нет оценок</p>"""
        self.assertIn(shop_name, html)
        self.assertIn(shop_desc_short, html)
        self.assertNotIn(shop_desc_full, rating)
        self.assertIn(rating, html)

    def test_shops_order(self):
        soup = BeautifulSoup(self.client.get('/').content, 'html.parser')
        shop_links = []
        for link in soup.find_all('a'):
            if 'shop' in link.text:
                shop_links.append(link.text)
        self.assertEqual(shop_links[0], 'good_shop')
        self.assertEqual(shop_links[1], 'very_good_shop')


class TestShopPage(TestCase):

    @classmethod
    def setUpTestData(cls):
        shop_properties = {'name': 'test_shop_1',
                           'short_description': 'some short description',
                           'full_description': 'some description but longer'}
        shop = ShopModel.objects.create(**shop_properties)
        category = GoodsCategoryModel.objects.create(category_name='some category')
        goods_properties = {'name': 'A fine goods',
                            'category': category,
                            'shop': shop,
                            'vendor_code': 123456,
                            'price': 1000,
                            'description': "A really great and cheap goods!"}
        GoodsModel.objects.create(**goods_properties)

    def test_correct_url(self):
        found = self.client.get('/shops/test_shop_1/')
        self.assertEqual(found.status_code, 200)

    def test_correct_view(self):
        found = resolve('/shops/test_shop_1/')
        self.assertEqual(found.func.__name__, ShopPageView.as_view().__name__)

    def test_correct_template(self):
        found = self.client.get('/shops/test_shop_1/')
        self.assertTemplateUsed(found, 'app_shops/shop_page.html')

    def test_correct_description(self):
        found = self.client.get('/shops/test_shop_1/')
        html = found.content.decode('utf-8')
        short_description = 'some short description'
        full_description = 'some description but longer'
        self.assertNotIn(short_description, html)
        self.assertIn(full_description, html)

    def test_goods_link(self):
        found = self.client.get('/shops/test_shop_1/')
        html = found.content.decode('utf-8')
        name = '''<li>Название: <a href="123456">A fine goods</a></li>'''
        self.assertIn(name, html)

    def test_goods_elements(self):
        found = self.client.get('/shops/test_shop_1/')
        html = found.content.decode('utf-8')
        goods = GoodsModel.objects.get(name='A fine goods')
        category = goods.category.category_name
        shop = '<li>'+str(goods.shop.name)+'</li>'
        vendor_code = '123456'
        price = '1000'
        self.assertIn(category, html)
        self.assertNotIn(shop, html)
        self.assertIn(vendor_code, html)
        self.assertIn(price, html)

    def test_goods_elements_order(self):
        soup = BeautifulSoup(self.client.get('/shops/test_shop_1/').content, 'html.parser')
        goods_properties = []
        for goods_info in soup.find_all('ul', {'class': "goods_properties"}):
            for element in goods_info.find_all('li'):
                goods_properties.append(element.text)
        goods = GoodsModel.objects.get(name='A fine goods')
        category = goods.category.category_name
        vendor_code = '123456'
        price = '1000'
        self.assertIn(goods.name, goods_properties[0])
        self.assertIn(category, goods_properties[1])
        self.assertIn(price, goods_properties[2],)
        self.assertIn(vendor_code, goods_properties[3])
        self.assertIn("У этого товара ещё нет оценок", goods_properties[4])


class TestGoodsPage(TestCase):

    @classmethod
    def setUpTestData(cls):
        shop_properties = {'name': 'test_shop_1',
                           'short_description': 'some description',
                           'full_description': 'some description but longer'}
        shop = ShopModel.objects.create(**shop_properties)
        category = GoodsCategoryModel.objects.create(category_name='some category')
        goods_properties = {'name': 'A fine goods',
                            'category': category,
                            'shop': shop,
                            'vendor_code': 123456,
                            'price': 1000,
                            'description': "A really great and cheap goods!",
                            'stock': 2}
        GoodsModel.objects.create(**goods_properties)

    def test_correct_url(self):
        found = self.client.get('/shops/test_shop_1/123456/')
        self.assertEqual(found.status_code, 200)

    def test_correct_view(self):
        found = resolve('/shops/test_shop_1/123456/')
        self.assertEqual(found.func, goods_page_view)

    def test_correct_html(self):
        found = self.client.get('/shops/test_shop_1/123456/')
        self.assertTemplateUsed(found, 'app_shops/goods_page.html')

    def test_elements(self):
        found = self.client.get('/shops/test_shop_1/123456/')
        html = found.content.decode('utf-8')
        shop = '''<p><a href="/shops/test_shop_1">Назад в магазин</a></p>'''
        description = 'A really great and cheap goods!'
        price = '1000'
        vendor_code = '123456'
        self.assertIn(shop, html)
        self.assertIn(description, html)
        self.assertIn(price, html)
        self.assertIn(vendor_code, html)

    def test_elements_order(self):
        soup = BeautifulSoup(self.client.get('/shops/test_shop_1/123456/').content, 'html.parser')
        goods_properties = []
        for item in soup.find_all('p'):
            goods_properties.append(item.text)
        shop = 'Назад в магазин'
        description = 'A really great and cheap goods!'
        price = 'Цена: 1000,0'
        vendor_code = 'Артикул: 123456'
        self.assertEqual(goods_properties[1], description)
        self.assertEqual(goods_properties[2], price)
        self.assertEqual(goods_properties[3], vendor_code)
        self.assertEqual(goods_properties[4], 'Количество: 2')
        self.assertEqual(goods_properties[5], shop)

    def test_no_buy_for_anonimus(self):
        found = self.client.get('/shops/test_shop_1/123456/')
        html = found.content.decode('utf-8')
        button = '''<button>Купить</button>'''
        self.assertNotIn(button, html)

    def test_buy_for_authenticated(self):
        user_data = {'username': 'user_1',
                     'password': "glavryiba"}
        TestMainPage.user = User.objects.create(**user_data)
        self.client.force_login(User.objects.get(username='user_1'))
        found = self.client.get('/shops/test_shop_1/123456/')
        html = found.content.decode('utf-8')
        button = '''<button>Купить</button>'''
        self.assertIn(button, html)

    def test_no_buying_button(self):
        user_data = {'username': 'user_1',
                     'password': "glavryiba"}
        TestMainPage.user = User.objects.create(**user_data)
        self.client.force_login(User.objects.get(username='user_1'))
        goods = GoodsModel.objects.get(vendor_code='123456')
        goods.stock = F('stock') - 2
        goods.save()
        found = self.client.get('/shops/test_shop_1/123456/')
        html = found.content.decode('utf-8')
        button = '''<button>Купить</button>'''
        self.assertNotIn(button, html)
        text = "К сожалению, данный товар закончился в этом магазине"
        self.assertIn(text, html)


class TestGoodsListPage(TestCase):

    @classmethod
    def setUpTestData(cls):
        shop_properties = {'name': 'test_shop_1',
                           'short_description': 'some description',
                           'full_description': 'some description but longer'}
        shop = ShopModel.objects.create(**shop_properties)
        category = GoodsCategoryModel.objects.create(category_name='some category')
        goods_properties = {'name': 'A fine goods',
                            'category': category,
                            'shop': shop,
                            'vendor_code': 123456,
                            'price': 1000,
                            'description': "A really great and cheap goods!"}
        GoodsModel.objects.create(**goods_properties)

    def test_correct_url(self):
        found = self.client.get('/goods_list/?goods_name=A fine goods/')
        self.assertEqual(found.status_code, 200)

    def test_correct_html(self):
        found = self.client.get('/goods_list/?goods_name=A fine goods/')
        self.assertTemplateUsed(found, 'app_shops/goods_list_page.html')

    def test_correct_output(self):
        found = self.client.get('/goods_list/?goods_name=A fine goods')
        html = found.content.decode('utf-8')
        self.assertIn('test_shop_1', html)
        link = '/shops/test_shop_1/'
        self.assertIn(link, html)

    def test_incorrect_output(self):
        found = self.client.get('/goods_list/?goods_name=A fine shop')
        html = found.content.decode('utf-8')
        self.assertIn('По вашему запросу ничего не найдено', html)



