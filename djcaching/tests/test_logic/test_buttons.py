from selenium import webdriver
from django.test import TestCase
from django.contrib.auth.models import User
from app_users.models import CartModel
from app_shops.models import ShopModel, GoodsCategoryModel,GoodsModel
from selenium.webdriver.common.by import By


class TestUserProfileButtons(TestCase):

    @classmethod
    def setUpTestData(cls):
        user_data = {'username': 'user_1',
                     'password': "glavryiba"}
        User.objects.create(**user_data)

    def setUp(self):
        self.browser = webdriver.Firefox()

    def tearDown(self):
        self.browser.quit()

    def test_add_address_button(self):
        self.browser.get('http://localhost:8000/user_profile/user_1/')


class TestAddGoodsToCart(TestCase):

    @classmethod
    def setUpTestData(cls):
        user_data = {'username': 'user_1',
                     'password': "glavryiba"}
        user = User.objects.create(**user_data)
        CartModel.objects.create(user=user)
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

    def setUp(self):
        self.browser = webdriver.Firefox()

    def tearDown(self):
        self.browser.quit()

    # def test_add_goods_button(self):
    #     self.browser.get('http://localhost:8000//shops/test_shop_1/123456/')
    #     self.browser.find_element(By.XPATH, "//button[text()='Купить']").click()
    #     user = User.objects.get(username='user_1')
    #     goods = GoodsModel.objects.get(vendor_code=123456)
    #     self.assertEqual(user.cart.all.goods.all[0], goods)



