from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from django.shortcuts import get_object_or_404
from django.db import transaction
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from .models import Sweet, Purchase
from .serializers import SweetSerializer, PurchaseSerializer, UserRegisterSerializer
from django.db.models import Q
from rest_framework import viewsets
class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            "refresh": str(refresh),
            "access": str(refresh.access_token)
        }, status=status.HTTP_201_CREATED)
class SweetListCreateView(generics.ListCreateAPIView):
    queryset = Sweet.objects.all()
    serializer_class = SweetSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        qs = super().get_queryset()
        q = self.request.query_params
        name = q.get('name')
        category = q.get('category')
        price_min = q.get('price_min')
        price_max = q.get('price_max')

        if name:
            qs = qs.filter(name__icontains=name)
        if category:
            qs = qs.filter(category__iexact=category)
        if price_min:
            try:
                qs = qs.filter(price__gte=float(price_min))
            except ValueError:
                pass
        if price_max:
            try:
                qs = qs.filter(price__lte=float(price_max))
            except ValueError:
                pass
        return qs
class SweetDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Sweet.objects.all()
    serializer_class = SweetSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def delete(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return Response({"detail": "Only admin can delete sweets."}, status=status.HTTP_403_FORBIDDEN)
        return super().delete(request, *args, **kwargs)
class PurchaseView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @transaction.atomic
    def post(self, request, pk):
        sweet = get_object_or_404(Sweet, pk=pk)
        qty = int(request.data.get('quantity', 1))
        if qty <= 0:
            return Response({"detail": "Quantity must be positive."}, status=status.HTTP_400_BAD_REQUEST)
        if sweet.quantity < qty:
            return Response({"detail": "Not enough stock."}, status=status.HTTP_400_BAD_REQUEST)

        sweet.quantity -= qty
        sweet.save()

        purchase = Purchase.objects.create(sweet=sweet, user=request.user, quantity=qty)
        serializer = PurchaseSerializer(purchase)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
class RestockView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]

    @transaction.atomic
    def post(self, request, pk):
        sweet = get_object_or_404(Sweet, pk=pk)
        qty = int(request.data.get('quantity', 0))
        if qty <= 0:
            return Response({"detail": "Quantity must be positive."}, status=status.HTTP_400_BAD_REQUEST)
        sweet.quantity += qty
        sweet.save()
        serializer = SweetSerializer(sweet)
        return Response(serializer.data, status=status.HTTP_200_OK)

class IsAdminUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_staff

class SweetViewSet(viewsets.ModelViewSet):
    queryset = Sweet.objects.all()
    serializer_class = SweetSerializer
    permission_classes = [IsAdminUser]