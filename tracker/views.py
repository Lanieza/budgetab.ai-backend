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