from django.contrib.auth.models import User
from django.test import TestCase
from app_users.views import goods_delete_view
from app_users.models import Address, CartModel, PurchaseHistoryModel
from app_shops.models import ShopModel, GoodsModel, GoodsCategoryModel, RatingModel
from django.urls import resolve


class TestDeleteLogic(TestCase):

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
        goods = GoodsModel.objects.create(**goods_properties)
        user_data = {'username': 'user_1',
                     'password': "glavryiba"}
        user = User.objects.create(**user_data)
        cart = CartModel.objects.create(user=user)
        cart.goods.add(goods)
        PurchaseHistoryModel.objects.create(user=user)


    def test_correct_url(self):
        found = self.client.get('/user_profile/user_1/cart/1')
        self.assertEqual(found.status_code, 302)

    def test_correct_view(self):
        found = resolve('/user_profile/user_1/cart/1')
        self.assertEqual(found.func, goods_delete_view)


