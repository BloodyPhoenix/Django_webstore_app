from django.contrib import admin
from .models import ShopModel, GoodsModel, GoodsCategoryModel, CommentModel, RatingModel


class ShopModelAdmin(admin.ModelAdmin):
    pass


class GoodsModelAdmin(admin.ModelAdmin):
    pass


class GoodsCategoryModelAdmin(admin.ModelAdmin):
    pass


class CommentModelAdmin(admin.ModelAdmin):
    pass


class RatingModelAdmin(admin.ModelAdmin):
    pass


admin.site.register(ShopModel, ShopModelAdmin)

admin.site.register(GoodsModel, GoodsModelAdmin)

admin.site.register(GoodsCategoryModel, GoodsCategoryModelAdmin)

admin.site.register(CommentModel, CommentModelAdmin)

admin.site.register(RatingModel, RatingModelAdmin)
