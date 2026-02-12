from rest_framework import viewsets
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from .models import MemberProfile
from .serializers import MemberProfileSerializer

class MemberProfileViewSet(viewsets.ModelViewSet):
    queryset = MemberProfile.objects.select_related('user').all()
    serializer_class = MemberProfileSerializer
    parser_classes = [MultiPartParser, FormParser]

    def get_permissions(self):
        if self.action in ['me', 'update', 'partial_update']:
            return [IsAuthenticated()]
        return [AllowAny()]

    @action(detail=False, methods=['get', 'put'], permission_classes=[IsAuthenticated])
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
