from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.db.models import Sum
from .models import Donation
from .serializers import DonationSerializer

class DonationViewSet(viewsets.ModelViewSet):
    queryset = Donation.objects.all().order_by('-created_at')
    serializer_class = DonationSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        serializer.save(status='pending')

    @action(detail=False, methods=['get'])
    def total(self, request):
        total_amount = Donation.objects.filter(status='completed').aggregate(Sum('amount'))['amount__sum'] or 0
        total_donations = Donation.objects.filter(status='completed').count()
        return Response({'total_amount': total_amount, 'total_donations': total_donations})
