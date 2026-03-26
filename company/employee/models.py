from django.db import models
from django.contrib.auth.models import User
from manager.models import Product

# Create your models here.

class Register(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE)
    address=models.TextField()
    phonenumber=models.CharField(max_length=10)
    gender=models.CharField(max_length=10, blank=True)
    profilephoto=models.FileField(upload_to='profile')
    city=models.CharField(max_length=100, blank=True)
    state=models.CharField(max_length=100, blank=True)
    postal_code=models.CharField(max_length=10, blank=True)

    
    
class Cart(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)


class CartItem(models.Model):
    cart=models.ForeignKey(Cart,on_delete=models.CASCADE)    
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    quantity=models.IntegerField()
    

class Order(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    orderdate=models.DateTimeField(auto_now_add=True)
    deliverydate=models.DateTimeField(null=True, blank=True)
    carrier=models.CharField(max_length=100, blank=True)
    payment_date=models.DateTimeField(null=True, blank=True)
    total_amount=models.FloatField(default=0.0)
    orderstatus=models.CharField(max_length=20, default='pending')
    paymentstatus=models.CharField(max_length=20, default='')
    trackingid=models.CharField(max_length=100, blank=True)
    payment_method=models.CharField(max_length=50, blank=True)    
    
    
    
class OrderItem(models.Model):
    order=models.ForeignKey(Order,on_delete=models.CASCADE)
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    quantity=models.IntegerField()
    price=models.IntegerField()


class Wishlist(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    created_at=models.DateTimeField(auto_now_add=True)

# wishlist
# user
# product



# Review
# user,product,comment,rating

class review(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    comment=models.TextField(max_length=100)
    rating=models.CharField(max_length=100)
    