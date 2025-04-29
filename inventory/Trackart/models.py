
from django.db import models
from dashboard.models import CustomUser
# Create your models here.
class Products(models.Model):
    id = models.AutoField(primary_key=True)
    category=models.CharField(max_length = 100)
    sub_category=models.CharField(max_length=100)
    image_link=models.URLField()
    description=models.TextField()
    offer_price=models.IntegerField()
    original_price=models.IntegerField()
    discount=models.IntegerField()
    quantity=models.IntegerField(default=1)
    chooser=models.ManyToManyField(CustomUser)
    


class Wishlist(models.Model):
    id = models.AutoField(primary_key=True)
    category=models.CharField(max_length = 100)
    sub_category=models.CharField(max_length=100)
    image_link=models.URLField()
    description=models.TextField()
    offer_price=models.IntegerField()
    original_price=models.IntegerField()
    discount=models.IntegerField()
    quantity=models.IntegerField(default=1)
    chooser=models.ManyToManyField(CustomUser)



    def __str__(self):
        return self.category

