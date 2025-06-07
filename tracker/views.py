import csv
from django.http import HttpResponse
from .models import Entry
from django.utils.timezone import now
from rest_framework import generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import Entry
from .serializers import EntrySerializer
from .models import Budget
from .serializers import BudgetSerializer

class EntryListCreateView(generics.ListCreateAPIView):
    serializer_class = EntrySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Entry.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class EntryDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = EntrySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Entry.objects.filter(user=self.request.user)

class ExportCSVView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # Get query parameters for filtering (optional)
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        category = request.GET.get('category')

        # Filter entries based on the authenticated user and optional filters
        queryset = Entry.objects.filter(user=request.user)
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)
        if category:
            queryset = queryset.filter(category=category)

        # Create the CSV response
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="entries_{now().strftime("%Y%m%d%H%M%S")}.csv"'

        writer = csv.writer(response)
        # Write the header row
        writer.writerow(['Title', 'Amount', 'Entry Type', 'Category', 'Date', 'Notes'])

        # Write data rows
        for entry in queryset:
            writer.writerow([entry.title, entry.amount, entry.entry_type, entry.category, entry.date, entry.notes])

        return response

class BudgetView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Retrieve the budget for the authenticated user
        budget, created = Budget.objects.get_or_create(user=request.user)
        serializer = BudgetSerializer(budget)
        return Response(serializer.data)

    def post(self, request):
        # Update the budget for the authenticated user
        budget, created = Budget.objects.get_or_create(user=request.user)
        serializer = BudgetSerializer(budget, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)
    

from datetime import date, timedelta
from decimal import Decimal
import os
import requests

class AIInsightView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        today = date.today()
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=6)

        entries = Entry.objects.filter(
            user=user,
            entry_type='expense',
            date__range=[start_of_week, end_of_week]
        ).order_by('-date')

        total_expenses = sum(entry.amount for entry in entries)
        entries_data = EntrySerializer(entries, many=True).data

        budget = getattr(user, 'budget', None)
        weekly_limit = budget.weekly_limit if budget else Decimal('0.00')

        prompt = f"""
You are a financial assistant AI. Analyze the user's weekly expenses compared to their weekly budget.

Weekly Budget Limit: {weekly_limit}
Total Expenses This Week: {total_expenses}

This Week's Expense Entries:
{entries_data}

Give 3–5 helpful insights in plain language. Mention if they're under or over budget.
        """

        headers = {
            "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": os.getenv("OPENROUTER_MODEL", "deepseek/deepseek-r1:free"),
            "messages": [
                {"role": "system", "content": "You are a helpful financial assistant."},
                {"role": "user", "content": prompt}
            ]
        }

        try:
            res = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
            res.raise_for_status()
            insights = res.json()['choices'][0]['message']['content']
            return Response({
                "insights": insights,
                "summary": {
                    "weekly_limit": str(weekly_limit),
                    "total_expenses": str(total_expenses),
                    "start_of_week": str(start_of_week),
                    "end_of_week": str(end_of_week),
                }
            })

        except requests.exceptions.RequestException as e:
            return Response({"error": str(e)}, status=500)
