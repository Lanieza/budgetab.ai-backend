from django.db import models
from django.conf import settings

class Entry(models.Model):
    CATEGORY_CHOICES = (
        ('food', 'Food'),
        ('travel', 'Travel'),
        ('bills', 'Bills'),
        ('other', 'Other'),
    )

    ENTRY_TYPE_CHOICES = (
        ('income', 'Income'),
        ('expense', 'Expense'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    entry_type = models.CharField(max_length=10, choices=ENTRY_TYPE_CHOICES, default='expense')  # Field for income/expense
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, null=True, blank=True)
    title = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    notes = models.TextField(null=True, blank=True)  # Added notes field

    def __str__(self):
        return f"{self.title} - {self.amount} ({self.entry_type})"

class Budget(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='budget')
    weekly_limit = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    monthly_limit = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    annual_limit = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)

    def __str__(self):
        return f"Budget for {self.user.username}"