from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from advertisements.models import Advertisement, Favourites
from advertisements.serializers import AdvertisementSerializer, FavouritesSerializer
from advertisements.permissions import IsOwnerOrAdminOrReadOnly, IsOwnerOnly
from advertisements.filters import AdvertisementFilter


class AdvertisementViewSet(ModelViewSet):
    """ViewSet для объявлений."""

    queryset = Advertisement.objects.all()
    serializer_class = AdvertisementSerializer

    filter_backends = [DjangoFilterBackend]
    filterset_class = AdvertisementFilter


    def get_permissions(self):
        """Получение прав для действий."""

        if self.action in ["update", "partial_update", "destroy"]:
            return [IsOwnerOrAdminOrReadOnly()]

        elif self.action == "create":
            return [IsAuthenticated()]

        return []


class FavouritesViewSet(ModelViewSet):
    queryset = Favourites.objects.all()
    serializer_class = FavouritesSerializer

    permission_classes = [IsOwnerOnly]

    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['user']

