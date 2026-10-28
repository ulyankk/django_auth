from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from django.http import JsonResponse
from django.db import connection
from .models import Category, Ticket
from .serializers import (
    CategorySerializer,
    TicketSerializer,
)

def healthz(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            row = cursor.fetchone()
        
        if row and row[0] == 1:
            return JsonResponse({"status": "ok", "database": "connected"})
    except Exception as e:
        return JsonResponse({"status": "error", "detail": str(e)}, status=500)


@login_required(login_url="/admin/login/")
@ensure_csrf_cookie
def dashboard(request):
    return render(request, "tickets/dashboard.html")

class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]



class TicketViewSet(viewsets.ModelViewSet):
    serializer_class = TicketSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Ticket.objects.filter(
            owner=self.request.user
        ).select_related("category")

        status = self.request.query_params.get("status")
        if status:
            queryset = queryset.filter(status=status)

        return queryset.order_by("-created_at")

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
