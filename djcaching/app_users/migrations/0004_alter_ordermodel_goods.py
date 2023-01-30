# Generated by Django 4.1.3 on 2022-12-10 18:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_shops', '0003_alter_goodsmodel_stock'),
        ('app_users', '0003_userprofile_money_spent_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ordermodel',
            name='goods',
            field=models.ManyToManyField(max_length=15000, related_name='order', to='app_shops.goodsmodel', verbose_name='Товары'),
        ),
    ]
