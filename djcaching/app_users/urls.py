from django.urls import path
from . import views

urlpatterns = [
    path('registration/', views.user_register_view, name='users'),
    path('login/', views.UserLoginView.as_view(), name='users'),
    path('logout/', views.UserLogoutView.as_view(), name='users'),
    path('user_profile/<str:username>/', views.user_profile_view, name='users'),
    path('user_profile/<str:username>/add_address/', views.add_address_view, name='users'),
    path('user_profile/<str:username>/delete_<int:address_index>', views.delete_address_view, name='users'),
    path('user_profile/<str:username>/cart/', views.cart_page_view, name='users'),
    path('user_profile/<str:username>/cart/<int:i>', views.goods_delete_view, name='user'),
    path('user_profile/<str:username>/balance_replenish/', views.balance_replenish_view, name='user'),
    path('purchase_confirmed/', views.purchase_confirmed_view, name='purchase_confimed')
]