from django.test import TestCase
from django.contrib.auth.models import User
from app_shops.models import ShopModel, GoodsModel, GoodsCategoryModel, RatingModel
from app_users.models import CartModel, PurchaseHistoryModel, BalanceModel, UserProfile, UserStatusModel


class TestUserStatusChange(TestCase):

    @classmethod
    def setUpTestData(cls):
        rating = {'average': 4.32}
        rating = RatingModel.objects.create(**rating)
        shop_1_data = {'name': 'test_shop_1',
                       'short_description': "Best prices!",
                       'full_description': 'We have great amount of goods and great prices for our customers!',
                       'rating': rating}
        shop = ShopModel.objects.create(**shop_1_data)
        category = GoodsCategoryModel.objects.create(category_name='some category')
        goods_properties = {'name': 'A fine goods',
                            'category': category,
                            'shop': shop,
                            'vendor_code': 123456,
                            'price': 2000,
                            'description': "A really great and cheap goods!",
                            'stock': 3}
        goods = GoodsModel.objects.create(**goods_properties)
        user_data = {'username': 'user_1',
                     'password': "glavryiba"}
        user = User.objects.create(**user_data)
        cart = CartModel.objects.create(user=user)
        cart.goods.add(goods)
        PurchaseHistoryModel.objects.create(user=user)
        BalanceModel.objects.create(user=user, money=5000)
        status = UserStatusModel.objects.create(status_name='Новый пользователь', status_requirement=0)
        UserStatusModel.objects.create(status_name='Член клуба', status_requirement=2000)
        UserStatusModel.objects.create(status_name='Вип-пользователь', status_requirement=5000)
        UserProfile.objects.create(user=user, first_name='Vanya', surname='Pechkin', user_status=status)

    def test_status_change(self):
        self.client.post('/user_profile/user_1/cart/', data={})
        user_profile = UserProfile.objects.get(first_name='Vanya')
        user_status = UserStatusModel.objects.get(user_profiles=user_profile)
        suggested_status = UserStatusModel.objects.get(status_name="Член клуба")
        self.assertEqual(user_status, suggested_status)



