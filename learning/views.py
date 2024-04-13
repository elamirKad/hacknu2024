from django.http import JsonResponse
from drf_yasg.openapi import Schema, TYPE_OBJECT, TYPE_INTEGER, TYPE_BOOLEAN, TYPE_STRING
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import permission_classes, api_view
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Experience, ReadingQuestion, GrammarQuestion, VocabularyQuestion, GrammarAnswer, VocabularyAnswer, \
    Lecture
from .serializers import ExperienceSerializer, ReadingQuestionSerializer, GrammarQuestionSerializer, \
    VocabularyQuestionSerializer, LectureSerializer


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

    level_descriptions = {
        1: 'Описание первого уровня',
        2: 'Описание второго уровня',
        3: 'Описание третьего уровня'
    }

    @staticmethod
    def get_minimal_level_name(level):
        return {
            1: 'Жауынгер +',
            2: 'Сарбаз +',
            3: 'Шаруа +'
        }.get(level, 'Unknown Level')

    @swagger_auto_schema(
        operation_description="Get questions by level: 1, 2, 3"
    )
    def get(self, request, level):
        user = request.user
        response_data = {}
        level_filter = [level]

        reading_questions = ReadingQuestion.objects.filter(level__in=level_filter)
        grammar_questions = GrammarQuestion.objects.filter(level__in=level_filter)
        vocabulary_questions = VocabularyQuestion.objects.filter(level__in=level_filter)
        lectures = Lecture.objects.filter(level__in=level_filter)

        response_data['reading_task'] = ReadingQuestionSerializer(reading_questions, many=True, context={'request': request}).data
        response_data['grammar_task'] = GrammarQuestionSerializer(grammar_questions, many=True, context={'request': request}).data
        response_data['vocabulary_task'] = VocabularyQuestionSerializer(vocabulary_questions, many=True, context={'request': request}).data
        response_data['lectures'] = LectureSerializer(lectures, many=True, context={'request': request}).data

        response_data['level_description'] = self.level_descriptions.get(level)
        response_data['minimal_level_name'] = self.get_minimal_level_name(level)

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
            serializer = ReadingQuestionSerializer(question, context={'request': request})
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
            serializer = GrammarQuestionSerializer(question, context={'request': request})
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
            serializer = VocabularyQuestionSerializer(question, context={'request': request})
            return Response(serializer.data)
        except VocabularyQuestion.DoesNotExist:
            return Response({"error": "Vocabulary question not found."}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@swagger_auto_schema(
    operation_description="Submit a grammar question answer",
    request_body=Schema(
        type=TYPE_OBJECT,
        properties={
            'question_id': Schema(type=TYPE_INTEGER, description='The ID of the grammar question'),
            'user_answer': Schema(type=TYPE_STRING, description='The user\'s answer to the question')
        }
    ),
    responses={200: Schema(
        type=TYPE_OBJECT,
        properties={
            'id': Schema(type=TYPE_INTEGER, description='The ID of the answer'),
            'correct': Schema(type=TYPE_BOOLEAN, description='Whether the answer is correct')
        }
    )}
)
def submit_grammar_answer(request):
    try:
        question_id = request.data.get('question_id')
        user_answer = request.data.get('user_answer')

        question = GrammarQuestion.objects.get(id=question_id)
        is_correct = question.correct_answer == user_answer

        answer, created = GrammarAnswer.objects.update_or_create(
            user=request.user,
            grammar_question=question,
            defaults={'user_answer': user_answer, 'correct': is_correct}
        )

        return JsonResponse({
            'id': answer.id,
            'correct': answer.correct
        }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

    except GrammarQuestion.DoesNotExist:
        return JsonResponse({'error': 'Grammar question not found.'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@swagger_auto_schema(
    operation_description="Submit a vocabulary question answer",
    request_body=Schema(
        type=TYPE_OBJECT,
        properties={
            'question_id': Schema(type=TYPE_INTEGER, description='The ID of the vocabulary question'),
            'user_answer': Schema(type=TYPE_STRING, description='The user\'s answer to the question')
        }
    ),
    responses={200: Schema(
        type=TYPE_OBJECT,
        properties={
            'id': Schema(type=TYPE_INTEGER, description='The ID of the answer'),
            'correct': Schema(type=TYPE_BOOLEAN, description='Whether the answer is correct')
        }
    )}
)
def submit_vocabulary_answer(request):
    try:
        question_id = request.data.get('question_id')
        user_answer = request.data.get('user_answer')

        question = VocabularyQuestion.objects.get(id=question_id)
        is_correct = question.correct_answer == user_answer

        answer, created = VocabularyAnswer.objects.update_or_create(
            user=request.user,
            vocabulary_question=question,
            defaults={'user_answer': user_answer, 'correct': is_correct}
        )

        return JsonResponse({
            'id': answer.id,
            'correct': answer.correct
        }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

    except VocabularyQuestion.DoesNotExist:
        return JsonResponse({'error': 'Vocabulary question not found.'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
