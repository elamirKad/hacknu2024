from django.http import JsonResponse
from drf_yasg.utils import swagger_auto_schema
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Experience, ReadingQuestion, GrammarQuestion, VocabularyQuestion
from .serializers import ExperienceSerializer, ReadingQuestionSerializer, GrammarQuestionSerializer, VocabularyQuestionSerializer


class UserExperienceView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Get the user's experience data",
        responses={200: ExperienceSerializer()}
    )
    def get(self, request):
        try:
            experience = Experience.objects.get(user=request.user)
            serializer = ExperienceSerializer(experience)
            return Response(serializer.data)
        except Experience.DoesNotExist:
            return Response({"error": "Experience data not found."}, status=status.HTTP_404_NOT_FOUND)


class GetQuestionsByLevelView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Get questions by level: 1, 2, 3"
    )
    def get(self, request, level):
        user = request.user
        response_data = {}

        if level == 3:
            level_filter = [1, 2]
        else:
            level_filter = [level]

        reading_questions = ReadingQuestion.objects.filter(level__in=level_filter)
        grammar_questions = GrammarQuestion.objects.filter(level__in=level_filter)
        vocabulary_questions = VocabularyQuestion.objects.filter(level__in=level_filter)

        response_data['reading_questions'] = ReadingQuestionSerializer(reading_questions, many=True, context={'request': request}).data
        response_data['grammar_questions'] = GrammarQuestionSerializer(grammar_questions, many=True, context={'request': request}).data
        response_data['vocabulary_questions'] = VocabularyQuestionSerializer(vocabulary_questions, many=True, context={'request': request}).data

        return JsonResponse(response_data)


class GetReadingQuestion(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Get a reading question by ID",
        responses={200: ReadingQuestionSerializer()}
    )
    def get(self, request, pk):
        try:
            question = ReadingQuestion.objects.get(pk=pk)
            serializer = ReadingQuestionSerializer(question)
            return Response(serializer.data)
        except ReadingQuestion.DoesNotExist:
            return Response({"error": "Reading question not found."}, status=status.HTTP_404_NOT_FOUND)


class GetGrammarQuestion(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Get a grammar question by ID",
        responses={200: GrammarQuestionSerializer()}
    )
    def get(self, request, pk):
        try:
            question = GrammarQuestion.objects.get(pk=pk)
            serializer = GrammarQuestionSerializer(question)
            return Response(serializer.data)
        except GrammarQuestion.DoesNotExist:
            return Response({"error": "Grammar question not found."}, status=status.HTTP_404_NOT_FOUND)


class GetVocabularyQuestion(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Get a vocabulary question by ID",
        responses={200: VocabularyQuestionSerializer()}
    )
    def get(self, request, pk):
        try:
            question = VocabularyQuestion.objects.get(pk=pk)
            serializer = VocabularyQuestionSerializer(question)
            return Response(serializer.data)
        except VocabularyQuestion.DoesNotExist:
            return Response({"error": "Vocabulary question not found."}, status=status.HTTP_404_NOT_FOUND)
