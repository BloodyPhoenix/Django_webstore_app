from django.test import TestCase
from django.contrib.auth.models import User
from app_users.models import BalanceModel, PurchaseHistoryModel, UserProfile


class TestBalanceReplenish(TestCase):

    @classmethod
    def setUpTestData(cls):
        user_data = {'username': 'user_1',
                     'password': "glavryiba"}
        user = User.objects.create(**user_data)
        UserProfile.objects.create(user=user, first_name='Vanya', surname='Pechkin')
        BalanceModel.objects.create(user=user)

    def test_balance_replenish(self):
        self.client.post('/user_profile/user_1/balance_replenish/', data={'cash_added': 1000})
        balance = User.objects.select_related('balance').get(username='user_1').balance
        self.assertEqual(balance.money, 1000.0)

    def test_balance_replenish_redirect(self):
        user= User.objects.get(username='user_1')
        PurchaseHistoryModel.objects.create(user=user)
        found = self.client.post('/user_profile/user_1/balance_replenish/', data={'cash_added': 0})
        self.assertRedirects(found, '/user_profile/user_1/')
