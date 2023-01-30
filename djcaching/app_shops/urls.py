from django.urls import path
from rest_framework import routers
from . import views
from .api import GoodsPageViewSet

router = routers.DefaultRouter()
router.register(r'goods_list', GoodsPageViewSet, basename='goods_list')

urlpatterns = [
    path('', views.MainPageView.as_view(), name='shops'),
    path(r'shops/<str:slug>/', views.ShopPageView.as_view(), name='shops'),
    path(r'shops/<str:shop_name>/<int:vendor_code>/', views.goods_page_view, name='goods'),
]
urlpatterns += router.urls
