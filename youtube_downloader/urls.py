from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse

# A simple root view
def home(request):
    return HttpResponse("Welcome to the YouTube Downloader API!")

urlpatterns = [
    path('admin/', admin.site.urls),  # Django admin interface
    path('api/', include('api.urls')),  # API routes
    path('', home, name='home'),  # Root URL
]
