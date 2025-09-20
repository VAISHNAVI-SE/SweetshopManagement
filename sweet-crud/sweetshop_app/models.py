from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator

class Sweet(models.Model):
    name = models.CharField(max_length=100, unique=True)
    category = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    quantity = models.PositiveIntegerField(default=0)  # no negatives
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.category})"

class Purchase(models.Model):
    sweet = models.ForeignKey(Sweet, on_delete=models.CASCADE, related_name='purchases')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='purchases')
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    purchased_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} bought {self.quantity} x {self.sweet.name}"
