from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=200,null=True)
    description = models.CharField(max_length=100,null=True)
    is_premium = models.BooleanField(default=False)
    def __str__(self):
        return self.name
    
    
    
class Product(models.Model):
    name = models.CharField(max_length=200,null=True)
    description = models.TextField()
    price = models.FloatField(max_length=50,null=True)
    stock = models.IntegerField(null=True)
    image = models.FileField(upload_to='media/products')
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    def get_rating(self):
        from django.apps import apps
        Review = apps.get_model('employee', 'review')
        reviews = Review.objects.filter(product=self)
        if not reviews.exists():
            return "☆☆☆☆☆"
        
        emoji_map = {"⭐️": 1, "⭐️⭐️": 2, "⭐️⭐️⭐️": 3, "⭐️⭐️⭐️⭐️": 4, "⭐️⭐️⭐️⭐️⭐️": 5}
        total = 0
        count = 0
        for r in reviews:
            val = emoji_map.get(r.rating, 0)
            if val > 0:
                total += val
                count += 1
        
        if count == 0:
            return "☆☆☆☆☆"
            
        avg = round(total / count)
        return "⭐️" * avg