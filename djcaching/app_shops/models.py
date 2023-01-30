from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User


class RatingModel(models.Model):
    one_star = models.IntegerField(verbose_name=_("Количество оценок 1"), null=True)
    two_stars = models.IntegerField(verbose_name=_("Количество оценок 2"), null=True)
    three_stars = models.IntegerField(verbose_name=_("Количество оценок 3"), null=True)
    four_stars = models.IntegerField(verbose_name=_("Количество оценок 4"), null=True)
    five_stars = models.IntegerField(verbose_name=_("Количество оценок 5"), null=True)
    average = models.FloatField(verbose_name=_("Средний рейтинг"), max_length=3)

    def __str__(self):
        return _("Средний рейтинг: ")+str(self.average)

    class Meta:
        verbose_name = _("Рейтинг")
        verbose_name_plural = _("Рейтинги")


class ShopModel(models.Model):
    name = models.CharField(max_length=100, verbose_name=_("Название магазина"), unique=True, db_index=True)
    short_description = models.CharField(max_length=500, verbose_name=_("Короткое описание"),
                                         help_text=_("Краткое описание, которое будет видно на главной странице сайта"))
    full_description = models.TextField(max_length=2000, verbose_name=_("Полное описание"),
                                        help_text=_("Полное описание, которое будет видно на странице магазина"))
    rating = models.OneToOneField(RatingModel, verbose_name=_("рейтинг"), on_delete=models.CASCADE, related_name='shop',
                                  null=True)

    class Meta:
        verbose_name = _("Магазин")
        verbose_name_plural = _("Магазины")


class GoodsCategoryModel(models.Model):
    category_name = models.CharField(max_length=100, verbose_name=_("Категория товара"))

    class Meta:
        verbose_name = _("Категория товаров")
        verbose_name_plural = _("Категории товаров")


class GoodsModel(models.Model):
    name = models.CharField(max_length=100, verbose_name=_("Название товара"))
    category = models.ForeignKey(GoodsCategoryModel, on_delete=models.CASCADE, related_name='goods')
    shop = models.ForeignKey(ShopModel, on_delete=models.CASCADE, related_name='goods')
    vendor_code = models.CharField(max_length=20, verbose_name=_("Артикул"))
    price = models.FloatField(max_length=15, verbose_name=_("Цена"))
    description = models.TextField(max_length=20000, verbose_name=_("Описание товара"))
    stock = models.IntegerField(verbose_name=_("Количество в магазине"), default=0)
    rating = models.OneToOneField(RatingModel, verbose_name=_("рейтинг"), on_delete=models.CASCADE, related_name='goods',
                                  null=True)

    class Meta:
        verbose_name = _("Товар")
        verbose_name_plural = _("Товары")
        ordering = ['price']


class CommentModel(models.Model):
    content = models.TextField(max_length=20000, verbose_name=_("Текст отзыва"))
    author = models.ForeignKey(User, null=True, on_delete=models.DO_NOTHING, verbose_name=_("Автор"))
    author_name = models.CharField(max_length=50, null=True, verbose_name=_("Имя автора"))
    goods = models.ForeignKey(GoodsModel, null=True, on_delete=models.CASCADE, verbose_name=_("Товар"))
    shop = models.ForeignKey(ShopModel, null=True, on_delete=models.CASCADE, verbose_name=_("Магазин"))

    class Meta:
        verbose_name = _("Комментарий")
        verbose_name_plural = _("Комментарии")


class PersonalOfferModel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='personal_offer',
                             verbose_name=_("Персональные акции и предложения"))
    shop = models.ForeignKey(ShopModel, on_delete=models.CASCADE, related_name='personal_offer',
                             verbose_name=_("Персональные акции и предложения"))
    goods = models.OneToOneField(GoodsModel, on_delete=models.CASCADE, related_name='personal_offer',
                             verbose_name=_("Персональные акции и предложения"))
    discount = models.IntegerField(verbose_name=_("Размер скидки"))


