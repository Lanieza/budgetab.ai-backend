from django.urls import path
from .views import EntryListCreateView, EntryDetailView, ExportCSVView, BudgetView

urlpatterns = [
    path('entries/', EntryListCreateView.as_view(), name='entry-list'),
    path('entries/<int:pk>/', EntryDetailView.as_view(), name='entry-detail'),
    path('entries/export/', ExportCSVView.as_view(), name='entry-export'),  # New export endpoint
    path('budget/', BudgetView.as_view(), name='budget'),
]