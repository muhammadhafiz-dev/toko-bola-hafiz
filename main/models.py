import uuid
from django.db import models
from django.contrib.auth.models import User

class Product(models.Model): 
    CATEGORY_CHOICES = [
        ('merchandise', 'Merchandise'),
        ('ball', 'Ball'),
        ('shoes', 'Shoes'),
        ('ticket', 'Ticket'),
        ('jersey', 'Jersey'),
        ('exclusive', 'Exclusive'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    price = models.IntegerField()
    description = models.TextField()
    thumbnail = models.URLField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    is_featured = models.BooleanField(default=False)

    product_views = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True) # Field created_at dan tidak dimasukkan ke list fields didalam forms.py karena ditambahkan secara otomatis.
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    
    def __str__(self):
        return self.name

    @property
    def is_product_hot(self):
        return self.product_views > 20
        
    def increment_views(self):  # ini bakal ada di def show_product di views.py
        self.product_views += 1  # ini dari product_views diatas dari models.py
        self.save()