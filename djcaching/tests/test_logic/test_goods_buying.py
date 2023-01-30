from django.test import TestCase
from django.contrib.auth.models import User
from app_shops.models import ShopModel, GoodsModel, GoodsCategoryModel, RatingModel
from app_users.models import CartModel, PurchaseHistoryModel, BalanceModel, UserProfile, UserStatusModel


class TestGoodsAddingToCart(TestCase):

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
                            'price': 1000,
                            'description': "A really great and cheap goods!",
                            'stock': 3}
        GoodsModel.objects.create(**goods_properties)
        user_data = {'username': 'user_1',
                     'password': "glavryiba"}
        user = User.objects.create(**user_data)
        CartModel.objects.create(user=user)

    def test_goods_adding_to_cart(self):
        user = User.objects.get(username='user_1')
        self.client.force_login(user)
        self.client.post('/shops/test_shop_1/123456/', data={})
        goods = GoodsModel.objects.get(name='A fine goods')
        cart_goods = GoodsModel.objects.get(cart=CartModel.objects.get(user=user))
        self.assertEqual(goods, cart_goods)
        self.assertEqual(int(goods.stock), 2)

    def test_goods_correct_redirect(self):
        user = User.objects.get(username='user_1')
        self.client.force_login(user)
        found = self.client.post('/shops/test_shop_1/123456/', data={})
        self.assertRedirects(found, '/shops/test_shop_1/123456/')

    def test_goods_stock_updated(self):
        user = User.objects.get(username='user_1')
        self.client.force_login(user)
        self.client.post('/shops/test_shop_1/123456/', data={})
        found = self.client.get('/shops/test_shop_1/123456/')
        html = found.content.decode('utf-8')
        self.assertIn('Количество: 2', html)


class TestGoodsPurchase(TestCase):

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
        status = UserStatusModel.objects.create(status_name='Новый пользователь', status_requirement=0)
        UserStatusModel.objects.create(status_name='Член клуба', status_requirement=2000)
        UserProfile.objects.create(user=user, first_name='Vanya', surname='Pechkin', user_status=status)
        BalanceModel.objects.create(user=user, money=1000)
        cart = CartModel.objects.create(user=user)
        cart.goods.add(goods)
        PurchaseHistoryModel.objects.create(user=user)

    def test_buying_successful(self):
        found = self.client.post('/user_profile/user_1/cart/', data={})
        user = User.objects.select_related('balance', 'cart', 'purchase_history').get(username='user_1')
        self.client.force_login(user)
        self.assertEqual(user.balance.money, 0)
        self.assertEqual(len(user.cart.goods.all()), 0)
        self.assertEqual(user.purchase_history.orders.get().goods.get(), GoodsModel.objects.get())
        self.assertRedirects(found, '/purchase_confirmed/')

    def test_buying_redirect(self):
        user = User.objects.get(username='user_1')
        self.client.force_login(user)
        found = self.client.post('/user_profile/user_1/cart/', data={})
        self.assertRedirects(found, '/purchase_confirmed/')








