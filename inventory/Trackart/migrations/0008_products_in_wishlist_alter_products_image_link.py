# Generated by Django 5.1.7 on 2025-04-14 18:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Trackart', '0007_alter_products_image_link'),
    ]

    operations = [
        migrations.AddField(
            model_name='products',
            name='in_wishlist',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='products',
            name='image_link',
            field=models.URLField(),
        ),
    ]
