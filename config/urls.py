from django.contrib import admin
from django.urls import include, path
from django.http import JsonResponse

def healthz(request):
    return JsonResponse({"status": "ok"})

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path("healthz/", healthz),
    path('', include('accounts.urls')),

    path('', include('tickets.urls')),
]