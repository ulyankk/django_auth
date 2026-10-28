from django.contrib import admin
from django.urls import include, path
from django.http import JsonResponse
from django.db import connection

def healthz(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            row = cursor.fetchone()
        
        if row and row[0] == 1:
            return JsonResponse({"status": "ok", "database": "connected"})
    except Exception as e:
        return JsonResponse({"status": "error", "detail": str(e)}, status=500)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path("healthz/", healthz),
    path('', include('accounts.urls')),
    path('', include('tickets.urls')),
]