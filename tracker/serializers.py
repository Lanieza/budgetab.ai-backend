from rest_framework import serializers
from .models import Entry
from .models import Budget

class EntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Entry
        fields = ['id', 'title', 'amount', 'date', 'category', 'entry_type', 'notes']

class BudgetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Budget
        fields = ['weekly_limit', 'monthly_limit', 'annual_limit']
