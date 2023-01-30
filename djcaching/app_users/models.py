import json
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from app_shops.models import GoodsModel


class UserStatusModel(models.Model):
    status_name = models.CharField(max_length=200, verbose_name=_("Название статуса пользователя"))
    status_requirement = models.IntegerField(default=0,
                                             verbose_name=_("Необходимое количество потраченных покупателем денег"))


class UserProfile(models.Model):
    first_name = models.CharField(max_length=50, verbose_name=_("Имя"))
    surname = models.CharField(max_length=100, verbose_name=_("Фамилия"))
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user_profile')
    user_status = models.ForeignKey(UserStatusModel, on_delete=models.DO_NOTHING, related_name="user_profiles",
                                    verbose_name=_("Статус пользователя"), null=True, blank=True)
    money_spent = models.IntegerField(default=0, verbose_name=_("Денег потрачено"))


class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='address')
    country = models.CharField(max_length=150, verbose_name=_('Страна'))
    town = models.CharField(max_length=150, verbose_name=_("Город"), help_text=_("Город"))
    street = models.CharField(max_length=200, verbose_name=_("Улица"), help_text=_("Улица"))
    house = models.CharField(max_length=25, verbose_name=_("Дом"), help_text=("Номер дома"))
    flat = models.IntegerField(verbose_name=_("Квартира"), help_text=("Номер квартиры"), null=True)


class CartModel(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    goods = models.ManyToManyField(GoodsModel, verbose_name=_("Товары"), max_length=15000, related_name='cart')

    def set_goods(self, goods):
        if self.goods:
            existing_goods = json.loads(str(self.goods))
            existing_goods.append(goods)
            self.goods = json.dumps(existing_goods)
        else:
            self.goods = json.dumps(goods)

    def get_goods(self):
        return json.loads(self.goods)


class PurchaseHistoryModel(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='purchase_history',
                                verbose_name=_("Пользователь"))


class OrderModel(models.Model):
    goods = models.ManyToManyField(GoodsModel, verbose_name=_("Товары"), max_length=15000, related_name='order')
    date = models.DateTimeField(auto_now_add=True, verbose_name=_("Дата покупки"))
    history = models.ForeignKey(PurchaseHistoryModel, on_delete=models.CASCADE, related_name='orders',
                                verbose_name=_("Заказ"))
    class Meta:
        ordering = ['date']

    def get_goods (self):
        goods_list = GoodsModel.objects.select_related('shop').only('shop__name', 'name', 'price', 'vendor_code').filter(order=self)
        goods_data = []
        for goods in goods_list:
            goods_properties = {'name': goods.name, 'price': goods.price, 'shop': goods.shop.name,
                                'vendor_code': goods.vendor_code}
            goods_properties['link'] = '/'+goods_properties['shop']+'/'+goods.vendor_code+'/'
            goods_data.append(goods_properties)
        return goods_data

    def __str__(self):
        goods_list = GoodsModel.objects.prefetch_related('shop').only('shop__name', 'name', 'price',
                                                                      'vendor_code').filter(order=self)
        string = 'Дата покупки: '+str(self.date)+'\n'
        for goods in goods_list:
            string += "Название: "+goods.name + '\n'
            string += "Цена: "+str(goods.price) + '\n'
            string += "Магазин: "+goods.shop.name + '\n'
            string += "Артикул: "+str(goods.vendor_code)+'\n'
        return string


class BalanceModel(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='balance', verbose_name=_("Пользователь"))
    money = models.IntegerField(verbose_name=_("Деньги"), default=0)


