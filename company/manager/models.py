from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=200,null=True)
    description = models.CharField(max_length=100,null=True)
    def __str__(self):
        return self.name
    
    
    
class Product(models.Model):
    name = models.CharField(max_length=200,null=True)
    description = models.TextField()
    price = models.FloatField(max_length=50,null=True)
    stock = models.IntegerField(null=True)
    image = models.ImageField(upload_to='media/products')
    category = models.ForeignKey(Category, on_delete=models.CASCADE)