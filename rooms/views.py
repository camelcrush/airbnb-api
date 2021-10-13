from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.pagination import PageNumberPagination
from .models import Room
from .serializers import RoomSerializer


class CustomPagination(PageNumberPagination):
    page_size = 20


class RoomsView(APIView):
    def get(self, request):
        paginator = CustomPagination()
        rooms = Room.objects.all()
        results = paginator.paginate_queryset(rooms, request)
        serializer = RoomSerializer(results, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        if not request.user.is_authnticated:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        serializer = RoomSerializer(data=request.data)
        if serializer.is_valid():
            room = serializer.save(user=request.user)
            room_serializer = RoomSerializer(room).data
            return Response(data=room_serializer, status=status.HTTP_200_OK)
        else:
            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RoomView(APIView):
    def get_room(self, pk):
        try:
            room = Room.objects.get(pk=pk)
            return room
        except Room.DoesNotExist:
            return None

    def get(self, request, pk):
        room = self.get_room(pk)
        if room is not None:
            serializer = RoomSerializer(room).data
            return Response(serializer)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def put(self, request, pk):
        room = self.get_room(pk)
        print(request.data.get("pk", None))
        if room is not None:
            if room.user != request.user:
                return Response(status=status.HTTP_403_FORBIDDEN)
            serializer = RoomSerializer(room, data=request.data, partial=True)
            if serializer.is_valid():
                room = serializer.save()
                return Response(RoomSerializer(room).data)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, pk):
        room = self.get_room(pk)
        if room is not None:
            if room.user != request.user:
                return Response(status=status.HTTP_403_FORBIDDEN)
            room.delelte()
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)


@api_view(["GET"])
def roomSearch(request):
    max_price = request.GET.get("max_price")
    min_price = request.GET.get("min_price")
    beds = request.GET.get("beds")
    bedrooms = request.GET.get("bedrooms")
    bathrooms = request.GET.get("bathrooms")
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
    try:
        rooms = Room.objects.filter(**filter_args)
    except ValueError:
        rooms = Room.objects.all()
    paginator = CustomPagination()
    results = paginator.paginate_queryset(rooms, request)
    serializer = RoomSerializer(results, many=True)
    return paginator.get_paginated_response(serializer.data)
