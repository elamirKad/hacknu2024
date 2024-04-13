from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Experience
from .serializers import ExperienceSerializer


class UserExperienceView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            experience = Experience.objects.get(user=request.user)
            serializer = ExperienceSerializer(experience)
            return Response(serializer.data)
        except Experience.DoesNotExist:
            return Response({"error": "Experience data not found."}, status=status.HTTP_404_NOT_FOUND)
