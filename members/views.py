from django.contrib.auth import get_user_model
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from .models import MemberProfile
from .serializers import MemberProfileSerializer


class MemberProfileViewSet(viewsets.ModelViewSet):
    queryset = MemberProfile.objects.select_related('user').all()
    serializer_class = MemberProfileSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        if self.action == 'me':
            return [IsAuthenticated()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        user_id = self.request.data.get('user_id')
        if user_id:
            User = get_user_model()
            serializer.save(user=User.objects.get(pk=user_id))
            return
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get', 'put', 'patch'], permission_classes=[IsAuthenticated])
    def me(self, request):
        profile, _ = MemberProfile.objects.get_or_create(user=request.user)
        if request.method == 'GET':
            serializer = self.get_serializer(profile)
            return Response(serializer.data)
        serializer = self.get_serializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        full_name = request.data.get('full_name')
        if full_name:
            request.user.full_name = full_name
            request.user.save(update_fields=['full_name'])
        return Response(serializer.data)
