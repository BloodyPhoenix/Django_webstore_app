from bs4 import BeautifulSoup
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import resolve
from django.core.cache import cache
from app_users.views import user_register_view, UserLoginView, user_profile_view, add_address_view, \
    delete_address_view, cart_page_view, balance_replenish_view, purchase_confirmed_view
from app_users.models import Address, CartModel, BalanceModel, PurchaseHistoryModel, OrderModel, UserProfile
from app_users.forms import LoginForm
from app_shops.models import ShopModel, GoodsModel, GoodsCategoryModel, RatingModel, PersonalOfferModel


class TestRegistrationPage(TestCase):

    def test_correct_url(self):
        found = self.client.get('/registration/')
        self.assertEqual(found.status_code, 200)

    def test_correct_view(self):
        found = resolve('/registration/')
        self.assertEqual(found.func, user_register_view)

    def test_correct_html(self):
        found = self.client.get('/registration/')
        self.assertTemplateUsed(found, 'app_users/register_page.html')

    def test_form_elements(self):
        soup = BeautifulSoup(self.client.get('/registration/').content, 'html.parser')
        inputs = []
        for element in soup.find_all('span', {'class': 'helptext'}):
            inputs.append(element)
        self.assertEqual(inputs[3].text, 'Имя')
        self.assertEqual(inputs[4].text, 'Фамилия')
        self.assertEqual(inputs[5].text, 'Страна')
        self.assertEqual(inputs[6].text, 'Город')
        self.assertEqual(inputs[7].text, 'Улица')
        self.assertEqual(inputs[8].text, 'Номер дома')
        self.assertEqual(inputs[9].text, 'Номер квартиры')


class TestLoginPage(TestCase):

    def test_correct_url(self):
        found = self.client.get('/login/')
        self.assertEqual(found.status_code, 200)

    def test_correct_view(self):
        found = resolve('/login/')
        self.assertEqual(found.func.__name__, UserLoginView.as_view().__name__)

    def test_correct_html(self):
        found = self.client.get('/login/')
        self.assertTemplateUsed(found, 'app_users/login_page.html')

    def test_form_on_page(self):
        found = self.client.get('/login/')
        html = found.content.decode('utf-8')
        form = LoginForm()
        self.assertIn(form.as_p(), html)


class TestUserProfilePage(TestCase):

    @classmethod
    def setUpTestData(cls):
        user_data = {'username': 'user_1',
                     'password': "glavryiba"}
        user = User.objects.create(**user_data)
        UserProfile.objects.create(user=user, first_name='Vanya', surname='Pechkin')
        PurchaseHistoryModel.objects.create(user=user)
        BalanceModel.objects.create(user=user)

    def tearDown(self):
        cache.clear()

    def test_correct_url(self):
        found = self.client.get('/user_profile/user_1/')
        self.assertEqual(found.status_code, 200)

    def test_correct_view(self):
        found = resolve('/user_profile/user_1/')
        self.assertEqual(found.func, user_profile_view)

    def test_correct_html(self):
        found = self.client.get('/user_profile/user_1/')
        self.assertTemplateUsed(found, 'app_users/user_profile_page.html')

    def test_add_address_button_exist(self):
        found = self.client.get('/user_profile/user_1/')
        html = found.content.decode('utf-8')
        button = '''<a href='/user_profile/user_1/add_address'><button>Добавить адрес</button></a>'''
        self.assertIn(button, html)

    def test_delete_address_button_not_exist_without_address(self):
        user = User.objects.get(username='user_1')
        self.client.force_login(user)
        found = self.client.get('/user_profile/user_1/')
        html = found.content.decode('utf-8')
        button = '''<button>Удалить адрес</button>'''
        self.assertNotIn(button, html)

    def test_delete_address_button_exist_if_address_exist(self):
        user = User.objects.get(username='user_1')
        data = {'user': user,
                'country': 'Russia',
                'town': 'Obochinsk',
                'street': 'Obyvnaya',
                'house': '1'}
        Address.objects.create(**data)
        self.client.force_login(user)
        found = self.client.get('/user_profile/user_1/')
        html = found.content.decode('utf-8')
        button = '''<button>Удалить адрес</button>'''
        self.assertIn(button, html)

    def test_no_purchase_history(self):
        cache.clear()
        user = User.objects.get(username='user_1')
        self.client.force_login(user)
        found = self.client.get('/user_profile/user_1/')
        html = found.content.decode('utf-8')
        text = 'Вы ещё ничего не купили.'
        self.assertIn(text, html)

    def test_purchase_history(self):
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
        goods = GoodsModel.objects.create(**goods_properties)
        history = PurchaseHistoryModel.objects.get(user=User.objects.get(username='user_1'))
        order = OrderModel.objects.create(history=history)
        order.goods.add(goods)
        user = User.objects.get(username='user_1')
        self.client.force_login(user)
        found = self.client.get('/user_profile/user_1/')
        html = found.content.decode('utf-8')
        text = 'A fine goods'
        self.assertIn(text, html)

    def test_no_personal_offers(self):
        user = User.objects.get(username='user_1')
        self.client.force_login(user)
        found = self.client.get('/user_profile/user_1/')
        html = found.content.decode('utf-8')
        text = "У вас сейчас нет персональных акций и предложений."
        self.assertIn(text, html)

    def test_personal_offer(self):
        user = User.objects.get(username='user_1')
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
        goods = GoodsModel.objects.create(**goods_properties)
        PersonalOfferModel.objects.create(user=user, shop=shop, goods=goods, discount=1000)
        user = User.objects.get(username='user_1')
        self.client.force_login(user)
        found = self.client.get('/user_profile/user_1/')
        html = found.content.decode('utf-8')
        text = "Магазин: test_shop_1"
        self.assertIn(text, html)

    def test_balance_on_page(self):
        user = User.objects.get(username='user_1')
        self.client.force_login(user)
        found = self.client.get('/user_profile/user_1/')
        html = found.content.decode('utf-8')
        text = "Ваш баланс: 0"
        self.assertIn(text, html)


class TestAddAddressPage(TestCase):

    @classmethod
    def setUpTestData(cls):
        user_data = {'username': 'user_1',
                     'password': "glavryiba"}
        User.objects.create(**user_data)

    def test_correct_url(self):
        found = self.client.get('/user_profile/user_1/add_address/')
        self.assertEqual(found.status_code, 200)

    def test_correct_view(self):
        found = resolve('/user_profile/user_1/add_address/')
        self.assertEqual(found.func, add_address_view)

    def test_correct_html(self):
        found = self.client.get('/user_profile/user_1/add_address/')
        self.assertTemplateUsed(found, 'app_users/add_address_page.html')


class TestAddressDeletePage(TestCase):

    @classmethod
    def setUpTestData(cls):
        user_data = {'username': 'user_1',
                     'password': "glavryiba"}
        user = User.objects.create(**user_data)
        data = {'user': user,
                'country': 'Russia',
                'town': 'Obochinsk',
                'street': 'Obyvnaya',
                'house': '1'}
        Address.objects.create(**data)

    def test_correct_url(self):
        user = User.objects.get(username='user_1')
        self.client.force_login(user)
        found = self.client.get('/user_profile/user_1/delete_1')
        self.assertEqual(found.status_code, 200)

    def test_correct_view(self):
        user = User.objects.get(username='user_1')
        self.client.force_login(user)
        found = resolve('/user_profile/user_1/delete_1')
        self.assertEqual(found.func, delete_address_view)

    def test_correct_html(self):
        user = User.objects.get(username='user_1')
        self.client.force_login(user)
        found = self.client.get('/user_profile/user_1/delete_1')
        self.assertTemplateUsed(found, 'app_users/delete_address_page.html')

    def test_address_elements(self):
        user = User.objects.get(username='user_1')
        self.client.force_login(user)
        found = self.client.get('/user_profile/user_1/delete_1')
        html = found.content.decode('utf-8')
        self.assertIn('Russia', html)


class TestCartPage(TestCase):

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
        goods_properties = {'name': 'Another fine goods',
                            'category': category,
                            'shop': shop,
                            'vendor_code': 123465,
                            'price': 1500,
                            'description': "A really great and cheap goods!"}
        GoodsModel.objects.create(**goods_properties)
        user_data = {'username': 'user_1',
                     'password': "glavryiba"}
        user = User.objects.create(**user_data)
        CartModel.objects.create(user=user)
        BalanceModel.objects.create(user=user)
        PurchaseHistoryModel.objects.create(user=user)

    def test_correct_url(self):
        found = self.client.get('/user_profile/user_1/cart/')
        self.assertEqual(found.status_code, 200)

    def test_correct_view(self):
        found = resolve('/user_profile/user_1/cart/')
        self.assertEqual(found.func, cart_page_view)

    def test_correct_html(self):
        found = self.client.get('/user_profile/user_1/cart/')
        self.assertTemplateUsed(found, 'app_users/cart_page.html')

    def test_no_goods_yet(self):
        found = self.client.get('/user_profile/user_1/cart/')
        html = found.content.decode('utf-8')
        text = "Ваша корзина пуста."
        self.assertIn(text, html)

    def test_goods_in_cart(self):
        user = User.objects.get(username='user_1')
        cart = CartModel.objects.get(user=user)
        goods = GoodsModel.objects.get(vendor_code='123456')
        cart.goods.add(goods)
        goods = GoodsModel.objects.get(vendor_code='123465')
        cart.goods.add(goods)
        found = self.client.get('/user_profile/user_1/cart/')
        html = found.content.decode('utf-8')
        text = 'A fine goods'
        self.assertIn(text, html)
        price = '1000'
        self.assertIn(price, html)
        button = '<button>Удалить</button>'
        self.assertIn(button, html)
        text = 'Another fine goods'
        self.assertIn(text, html)

    def test_not_enough_money(self):
        user = User.objects.get(username='user_1')
        cart = CartModel.objects.get(user=user)
        goods = GoodsModel.objects.get(vendor_code='123456')
        cart.goods.add(goods)
        found = self.client.get('/user_profile/user_1/cart/')
        html = found.content.decode('utf-8')
        text = 'У вас недостаточно средств для того, чтобы совершить покупку'
        self.assertIn(text, html)

    def test_enough_money(self):
        user = User.objects.get(username='user_1')
        cart = CartModel.objects.get(user=user)
        goods = GoodsModel.objects.get(vendor_code='123456')
        cart.goods.add(goods)
        goods = GoodsModel.objects.get(vendor_code='123456')
        cart.goods.add(goods)
        balance = BalanceModel.objects.get(user=user)
        balance.money = 2500.0
        balance.save()
        found = self.client.get('/user_profile/user_1/cart/')
        html = found.content.decode('utf-8')
        button = '''<a href="purchase_confirmation"><button>Оформить покупку</button></a>'''
        self.assertIn(button, html)


class TestPurchaseConfirmedPage(TestCase):
    @classmethod
    def setUpTestData(cls):
        user_data = {'username': 'user_1',
                     'password': "glavryiba"}
        user = User.objects.create(**user_data)
        history = PurchaseHistoryModel.objects.create(user=user)
        order = OrderModel.objects.create(history=history)
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
        goods = GoodsModel.objects.create(**goods_properties)
        order.goods.add(goods)
        goods_properties = {'name': 'Another fine goods',
                            'category': category,
                            'shop': shop,
                            'vendor_code': 123465,
                            'price': 1500,
                            'description': "A really great and cheap goods!"}
        goods = GoodsModel.objects.create(**goods_properties)
        order.goods.add(goods)

    def setUp(self):
        self.client.force_login(User.objects.get(username='user_1'))

    def test_correct_url(self):
        found = self.client.get('/purchase_confirmed/')
        self.assertEqual(found.status_code, 200)

    def test_correct_view(self):
        found = resolve('/purchase_confirmed/')
        self.assertEqual(found.func, purchase_confirmed_view)

    def test_correct_template(self):
        found = self.client.get('/purchase_confirmed/')
        self.assertTemplateUsed(found, 'app_users/purchase_confirmed.html')

    def test_elements_on_page(self):
        found = self.client.get('/purchase_confirmed/')
        goods_1 = GoodsModel.objects.select_related('shop').only('shop__name', 'name', 'price', 'vendor_code').get(name='A fine goods')
        html = found.content.decode('utf-8')
        self.assertIn(goods_1.name, html)
        self.assertIn('1000,0', html)
        self.assertIn(goods_1.shop.name, html)
        self.assertIn(str(goods_1.vendor_code), html)
        self.assertIn('Another fine goods', html)

    def test_correct_order(self):
        user = User.objects.get(username='user_1')
        goods = GoodsModel.objects.get(name='A fine goods')
        history = PurchaseHistoryModel.objects.get(user=user)
        order = OrderModel.objects.create(history=history)
        order.goods.add(goods)
        found = self.client.get('/purchase_confirmed/')
        html = found.content.decode('utf-8')
        self.assertNotIn('Another fine goods', html)


class TestBalanceReplenishPage(TestCase):

    @classmethod
    def setUpTestData(cls):
        user_data = {'username': 'user_1',
                     'password': "glavryiba"}
        user = User.objects.create(**user_data)
        BalanceModel.objects.create(user=user)

    def test_correct_url(self):
        found = self.client.get('/user_profile/user_1/balance_replenish/')
        self.assertEqual(found.status_code, 200)

    def test_correct_view(self):
        found = resolve('/user_profile/user_1/balance_replenish/')
        self.assertEqual(found.func, balance_replenish_view)

    def test_correct_html(self):
        found = self.client.get('/user_profile/user_1/balance_replenish/')
        self.assertTemplateUsed(found, 'app_users/balance_replenish_page.html')

    def test_correct_field(self):
        found = self.client.get('/user_profile/user_1/balance_replenish/')
        text = "Сколько денег вы хотите внести?"
        html = found.content.decode('utf-8')
        self.assertIn(text, html)
        self.assertIn('Сейчас на вашем счету: 0', html)








