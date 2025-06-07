from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse

def root_view(request):
    return HttpResponse("Backend API is running.")

urlpatterns = [
    path('', root_view),
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('api/tracker/', include('tracker.urls')), 
    path('api/accounts/', include('accounts.urls')),
]
