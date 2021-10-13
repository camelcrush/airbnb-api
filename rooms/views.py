from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.pagination import PageNumberPagination
from rest_framework import permissions
from .models import Room
from .serializers import RoomSerializer
from .permissions import IsOwner


class RoomViewSet(ModelViewSet):

    queryset = Room.objects.all()
    serializer_class = RoomSerializer

    def get_permissions(self):

        if self.action == "list" or self.action == "retrieve":
            permission_classes = [permissions.AllowAny]
        elif self.action == "create":
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [IsOwner]

        return [permission() for permission in permission_classes]


@api_view(["GET"])
def room_search(request):
    max_price = request.GET.get("max_price", None)
    min_price = request.GET.get("min_price", None)
    beds = request.GET.get("beds", None)
    bedrooms = request.GET.get("bedrooms", None)
    bathrooms = request.GET.get("bathrooms", None)
    lat = request.GET.get("lat", None)
    lng = request.GET.get("lng", None)
    filter_args = {}
    if max_price is not None:
        filter_args["price__lte"] = max_price
    if min_price is not None:
        filter_args["price__gte"] = min_price
    if beds is not None:
        filter_args["beds__gte"] = beds
    if bedrooms is not None:
        filter_args["bedrooms__gte"] = bedrooms
    if bathrooms is not None:
        filter_args["bathrooms__gte"] = bathrooms
    if lat is not None and lng is not None:
        filter_args["lat__gte"] = float(lat) - 0.005
        filter_args["lat__lte"] = float(lat) + 0.005
        filter_args["lng__gte"] = float(lng) - 0.005
        filter_args["lng__lte"] = float(lng) + 0.005
    try:
        rooms = Room.objects.filter(**filter_args)
    except ValueError:
        rooms = Room.objects.all()
    paginator = CustomPagination()
    results = paginator.paginate_queryset(rooms, request)
    serializer = RoomSerializer(results, many=True)
    return paginator.get_paginated_response(serializer.data)
