from django.db.models import F
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views.generic import ListView, DetailView
from django.db import transaction
from .models import ShopModel, GoodsModel


class MainPageView(ListView):
    template_name = 'app_shops/main_page.html'
    model = ShopModel
    context_object_name = 'shops_list'

    def get_ordering(self):
        ordering = self.request.GET.get('ordering', 'name')
        return ordering


class ShopPageView(DetailView):
    template_name = 'app_shops/shop_page.html'
    model = ShopModel
    context_object_name = 'shop'
    slug_field = 'name'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['goods_list'] = GoodsModel.objects.filter(shop=self.object)
        return context


def goods_page_view(request, shop_name, vendor_code):
    shop = ShopModel.objects.get(name=shop_name)
    goods = shop.goods.get(vendor_code=vendor_code)
    shop_link = '/shops/'+shop.name
    context = {'goods': goods,
              'shop_link': shop_link}
    if request.method == 'POST':
        with transaction.atomic():
            cart = request.user.cart
            cart.goods.add(goods)
            goods.stock = F('stock') - 1
            goods.save()
            return HttpResponseRedirect('/shops/test_shop_1/123456/')
    return render(request, 'app_shops/goods_page.html', context=context)

