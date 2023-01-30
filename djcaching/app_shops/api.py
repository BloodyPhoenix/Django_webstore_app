from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.renderers import TemplateHTMLRenderer
from .models import GoodsModel
from .serializers import GoodsSerializer


class TenObjectsPagination(PageNumberPagination):
    """Pagination class to display ten items per page"""
    page_size = 10
    page_query_param = 'page_size'
    max_page_size = 100


class GoodsPageViewSet(viewsets.ModelViewSet):
    serializer_class = GoodsSerializer
    pagination_class = TenObjectsPagination
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'app_shops/goods_list_page.html'
    
    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        if request.accepted_renderer.format == 'html':
            result = self.get_queryset()
            context = {'goods_name': self.request.query_params.get('goods_name'), 'goods_list': result, }
            return Response(context, template_name='app_shops/goods_list_page.html')
        return response

    def get_queryset(self):
        goods_name = self.request.query_params.get('goods_name')
        queryset = GoodsModel.objects.select_related('shop').filter(name__icontains=goods_name).only('name', 'shop__name', 'price')
        return queryset

