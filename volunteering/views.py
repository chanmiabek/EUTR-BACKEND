from rest_framework import viewsets
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Opportunity, Signup
from .serializers import OpportunitySerializer, SignupSerializer


class OpportunityViewSet(viewsets.ModelViewSet):
    queryset = Opportunity.objects.filter(is_active=True).order_by("-created_at")
    serializer_class = OpportunitySerializer
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def signup(self, request, pk=None):
        opportunity = self.get_object()
        serializer = SignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        Signup.objects.create(
            user=request.user,
            opportunity=opportunity,
            message=serializer.validated_data.get("message", ""),
        )
        return Response({"detail": "Signed up successfully."})
