from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Experience, ReadingQuestion, GrammarQuestion, VocabularyQuestion
from .serializers import ExperienceSerializer, ReadingQuestionSerializer, GrammarQuestionSerializer, VocabularyQuestionSerializer


class UserExperienceView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            experience = Experience.objects.get(user=request.user)
            serializer = ExperienceSerializer(experience)
            return Response(serializer.data)
        except Experience.DoesNotExist:
            return Response({"error": "Experience data not found."}, status=status.HTTP_404_NOT_FOUND)


class GetQuestionsByLevelView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, level):
        user = request.user
        response_data = {}

        reading_questions = ReadingQuestion.objects.filter(level__lte=level if level != 3 else 3)
        grammar_questions = GrammarQuestion.objects.filter(level__lte=level if level != 3 else 3)
        vocabulary_questions = VocabularyQuestion.objects.filter(level__lte=level if level != 3 else 3)

        response_data['reading_questions'] = ReadingQuestionSerializer(reading_questions, many=True, context={'request': request}).data
        response_data['grammar_questions'] = GrammarQuestionSerializer(grammar_questions, many=True, context={'request': request}).data
        response_data['vocabulary_questions'] = VocabularyQuestionSerializer(vocabulary_questions, many=True, context={'request': request}).data

        return JsonResponse(response_data)
