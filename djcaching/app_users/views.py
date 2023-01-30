import logging

from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.auth.views import LogoutView, LoginView
from django.db.models import F
from django.shortcuts import render, redirect
from django.core.cache import cache
from django.db import transaction
from .forms import LoginForm, RegisterForm, AddAddressForm, BalanceReplenishForm
from .models import UserProfile, Address, CartModel, PurchaseHistoryModel, OrderModel, BalanceModel, UserStatusModel
from app_shops.models import GoodsModel, PersonalOfferModel


logger = logging.getLogger(__name__)


def user_register_view(request):
    form = RegisterForm()
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            name = form.cleaned_data.get('name')
            surname = form.cleaned_data.get('surname')
            UserProfile.objects.create(user=user, name=name, surname=surname)
            country = form.cleaned_data.get('country')
            town = form.cleaned_data.get('town'),
            street = form.cleaned_data.get('street')
            house = form.cleaned_data.get('house')
            if 'flat' in form.cleaned_data:
                flat = form.cleaned_data.get('flat')
                Address.objects.create(user=user, country=country, town=town, street=street, house=house, flat=flat)
            else:
                Address.objects.create(user=user, country=country, town=town, street=street, house=house)
            CartModel.objects.create(user=user)
            PurchaseHistoryModel.objects.create(user=user)
            BalanceModel.objects.create(user=user)
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('/')
        else:
            form = RegisterForm()
    return render(request, 'app_users/register_page.html', {'form': form})


class UserLoginView(LoginView):

    template_name = 'app_users/login_page.html'
    redirect_authenticated_user = True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = LoginForm()
        return context


class UserLogoutView(LogoutView):
    pass


def user_profile_view(request, username):
    add_address_link = '/user_profile/'+username+'/add_address'
    user = User.objects.get(username=username)
    address_list = Address.objects.filter(user=user)
    address_data = {}
    page_address = 'delete_'
    number = 1
    for address in address_list:
        address_data[address] = page_address+str(number)
        number += 1
    balance = BalanceModel.objects.get(user=user).money
    history = PurchaseHistoryModel.objects.get(user=user)
    orders = []
    for order in history.orders.all():
        orders.append(order)
    personal_offers = []
    if cache.get('personal_offers') is None:
        try:
            offers = PersonalOfferModel.objects.filter(user=user)
            for offer in offers:
                personal_offers.append(offer)
        finally:
            cache.add('personal_offers', personal_offers, timeout=600)
    personal_offers = cache.get('personal_offers')
    if user.user_profile.user_status:
        user_status = user.user_profile.user_status.status_name
    else:
        user_status = "Статусная система пользовтаелей пока не поддерживается"
    return render(request, 'app_users/user_profile_page.html', context={'add_address_link': add_address_link,
                                                                            'address_data': address_data,
                                                                            'balance': balance,
                                                                            'orders': orders,
                                                                            'personal_offers': personal_offers,
                                                                            'user_status': user_status})


def add_address_view(request, username):
    form = AddAddressForm()
    if request.method == 'POST':
        form = AddAddressForm(request.POST)
        if form.is_valid():
            user = request.user
            country = form.cleaned_data.get('country')
            town = form.cleaned_data.get('town'),
            street = form.cleaned_data.get('street')
            house = form.cleaned_data.get('house')
            if 'flat' in form.cleaned_data:
                flat = form.cleaned_data.get('flat')
                Address.objects.create(user=user, country=country, town=town, street=street, house=house, flat=flat)
            else:
                Address.objects.create(user=user, country=country, town=town, street=street, house=house)
            return redirect('/user_profile/'+username+'/')
        else:
            form = AddAddressForm()
    return render(request, 'app_users/add_address_page.html', {'form': form})


def delete_address_view(request, username, address_index):
    user = User.objects.get(username=username)
    address_list = []
    for address in Address.objects.filter(user=user):
        address_list.append(address)
    index = address_index - 1
    address = address_list[index]
    go_back_link = '/user_profile/' + username + '/'
    if request.method == 'POST':
        address.delete()
        return redirect(go_back_link)
    go_back_link = '/user_profile/'+username+'/'
    return render(request, 'app_users/delete_address_page.html', context={'address': address,
                                                                          'go_back_link': go_back_link})


def cart_page_view(request, username):
    user = User.objects.get(username=username)
    cart = CartModel.objects.get(user=user)
    goods_data = {}
    i = 1
    goods = GoodsModel.objects.filter(cart=cart)
    price = 0
    for one_good in goods:
        delete_link = '/user_profile/' + username + '/cart/'+str(i)
        goods_data[one_good] = delete_link
        i += 1
        price += one_good.price
    balance = BalanceModel.objects.get(user=user)
    if balance.money < price:
        not_enough_money = True
    else:
        not_enough_money = False
    context = {'money': balance.money, 'goods': goods_data, 'price': price, 'not_enough_money': not_enough_money}
    if request.method == "POST":
        with transaction.atomic():
            history = PurchaseHistoryModel.objects.get(user=user)
            order = OrderModel.objects.create(history=history)
            for goods in goods:
                order.goods.add(goods)
            cart.goods.clear()
            user_profile = UserProfile.objects.get(user=user)
            try:
                user_status = user_profile.user_status
                next_status = UserStatusModel.objects.filter(status_requirement__gt=user_status.status_requirement).first()
                if next_status.status_requirement <= user_profile.money_spent + price:
                    user_profile.user_status = next_status
                    user_profile.save()
                    logger.info(f"Пользователь {username} получил статус {next_status}")
            except Exception as exeption:
                print('Something wrong with user status system')
                print(exeption, exeption.args)
            finally:
                balance.money = F('money') - price
                balance.save()
                user_profile.money_spent = F('money_spent') + price
                user_profile.save()
                logger.info(f"Пользователь {username} потратил {price} средств")
                return redirect('/purchase_confirmed/')
    return render(request, 'app_users/cart_page.html',
                  context=context)


def goods_delete_view(request, username, i):
    user = User.objects.get(username=username)
    cart = CartModel.objects.get(user=user)
    index = 1
    for goods in cart.goods.all():
        if index == i:
            cart.goods.remove(goods)
    return redirect('/user_profile/'+username+'/cart/')


def balance_replenish_view(request, username):
    balance = User.objects.select_related('balance').get(username=username).balance
    form = BalanceReplenishForm()
    context = {'current_balance': balance.money, 'add_form': form}
    if request.method == 'POST':
        form = BalanceReplenishForm(request.POST)
        if form.is_valid():
            cash_added = form.cleaned_data.get('cash_added')
            with transaction.atomic():
                balance.money = F('money') + cash_added
                balance.save()
                logger.info(f"Произведено пополнение счёта на {cash_added}")
            return redirect('/user_profile/'+username+'/')
    return render(request, 'app_users/balance_replenish_page.html', context=context)


def purchase_confirmed_view(request):
    history = PurchaseHistoryModel.objects.get(user=request.user)
    last_order = OrderModel.objects.prefetch_related('goods').filter(history=history).order_by('date').last()
    logger.info(f"Ползователь сделал заказ {last_order}")
    user_link = 'user_profile/'+request.user.username+'/'
    return render(request, 'app_users/purchase_confirmed.html', context={'user_link': user_link,
                                                                         'last_order': last_order.get_goods()})
