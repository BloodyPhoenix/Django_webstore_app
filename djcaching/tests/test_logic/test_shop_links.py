import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from django.test import TestCase
from app_shops.models import GoodsModel, GoodsCategoryModel, ShopModel


class TestGoodsListLinks(TestCase):

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

    def setUp(self):
        self.browser = webdriver.Firefox()

    def tearDown(self):
        self.browser.quit()
    #
    # def test_shop_link(self):
    #     self.browser.get('http://localhost:8000/goods_list/?goods_name=A fine')
    #     time.sleep(10)
    #     self.browser.find_element(By.PARTIAL_LINK_TEXT, "shops").click()
    #     self.assertEqual(self.browser.current_url, 'http://localhost:8000/shops/test_shop_1/')