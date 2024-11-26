from django.shortcuts import render
from rest_framework.views import APIView 
from rest_framework.response import Response 
from rest_framework import status 
from django.db.models import Q 
from .models import Room, Booking 
from rest_framework import viewsets
from datetime import datetime
from .serializers import RoomSerializer, BookingSerializer 
# Create your views here.

class AvailableRoomsAPIView(APIView):
    def get(self, request):
        # Retrieve query parameters
        check_in_date = request.query_params.get('check_in_date')
        check_out_date = request.query_params.get('check_out_date')
        room_type = request.query_params.get('type')
        min_price = request.query_params.get('min_price')
        max_price = request.query_params.get('max_price')

        # Validate required parameters
        if not check_in_date or not check_out_date:
            return Response(
                {"error": "Check-in and check-out dates are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validate date format
        try:
            check_in_date = datetime.strptime(check_in_date, "%Y-%m-%d").date()
            check_out_date = datetime.strptime(check_out_date, "%Y-%m-%d").date()
        except ValueError:
            return Response(
                {"error": "Invalid date format. Use YYYY-MM-DD."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Ensure check-in is before check-out
        if check_in_date >= check_out_date:
            return Response(
                {"error": "Check-out date must be after check-in date."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Filter out rooms already booked in the given date range
        booked_rooms = Booking.objects.filter(
            Q(check_in_date__lt=check_out_date) & Q(check_out_date__gt=check_in_date)
        ).values_list('room_id', flat=True)

        rooms = Room.objects.exclude(id__in=booked_rooms)

        # Apply additional filters
        if room_type:
            rooms = rooms.filter(type=room_type)
        if min_price:
            try:
                min_price = float(min_price)
                rooms = rooms.filter(price__gte=min_price)
            except ValueError:
                return Response(
                    {"error": "Invalid value for min_price. Must be a number."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        if max_price:
            try:
                max_price = float(max_price)
                rooms = rooms.filter(price__lte=max_price)
            except ValueError:
                return Response(
                    {"error": "Invalid value for max_price. Must be a number."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        # Serialize and return the data
        serializer = RoomSerializer(rooms, many=True)
        return Response(serializer.data)


class CreateBookingAPIView(APIView):
    def post(self, request):
        serializer = BookingSerializer(data=request.data)
        
        if serializer.is_valid():
            room = serializer.validated_data['room']
            check_in_date = serializer.validated_data['check_in_date']
            check_out_date = serializer.validated_data['check_out_date']

            # Prevent overlapping bookings
            overlapping_booking = Booking.objects.filter(
                room=room,
                check_in_date__lt=check_out_date,  # The room's booking starts before the new check-out
                check_out_date__gt=check_in_date   # The room's booking ends after the new check-in
            ).exists()

            if overlapping_booking:
                return Response(
                    {"error": "The room is already booked for the selected dates."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Save the booking if no overlap
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        # Return errors if serializer is not valid
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class Roomviewset(viewsets.ModelViewSet):
    serializer_class=RoomSerializer
    queryset=Room.objects.all()
