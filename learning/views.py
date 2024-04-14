import os

import requests
from django.conf import settings
from django.db import transaction
from django.http import JsonResponse
from django.utils.timezone import now
from drf_yasg import openapi
from drf_yasg.openapi import Schema, TYPE_OBJECT, TYPE_INTEGER, TYPE_BOOLEAN, TYPE_STRING
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import permission_classes, api_view
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from core.settings import MEDIA_ROOT
from .models import Experience, ReadingQuestion, Chat, GPTReport, Lessons, TaskAnswer, Tasks, Reading, ReadingAnswer
from .open import User, query_api, analyze_dialogue, check_reading_answers
from .serializers import ExperienceSerializer, GPTReportSerializer, LessonsSerializer, TasksSerializer, \
    ReadingSerializer, ReadingQuestionSerializer
from .tasks import post_text_to_service


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



@api_view(['POST'])
@permission_classes([IsAuthenticated])
@swagger_auto_schema(
    operation_description="Submit text to the chat API",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'prompt_kk': openapi.Schema(type=openapi.TYPE_STRING, description='The prompt in Kazakh language'),
        }
    ),
    responses={200: openapi.Response(
        description="Response from the chat API",
        schema=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'response': openapi.Schema(type=openapi.TYPE_STRING, description='The full response in Kazakh language'),
            }
        )
    )}
)
def send_text(request, chat_id):
    try:
        chat = Chat.objects.get(id=chat_id)
        user = User(id=chat_id, name="Эламир", surname="Кадыргалеев", age=20)
        prompt_kk = request.data.get('prompt_kk')
        print(prompt_kk)
        response_text = query_api(user, prompt_kk)

        url = "https://7a68-178-91-253-72.ngrok-free.app/synthesize/"
        data = {"text": response_text}
        post_text_to_service.delay(url, data)
        return JsonResponse({'response': response_text})

    except Chat.DoesNotExist:
        return JsonResponse({'error': 'Chat not found'}, status=404)


class CreateChatView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Create a new chat",
        request_body=Schema(
            type=TYPE_OBJECT,
            properties={
                'user_id': Schema(type=TYPE_INTEGER, description='The ID of the user')
            }
        ),
        responses={200: Schema(
            type=TYPE_OBJECT,
            properties={
                'id': Schema(type=TYPE_INTEGER, description='The ID of the chat')
            }
        )}
    )
    def post(self, request):
        user = request.user
        chat = Chat.objects.create(user=user)
        return JsonResponse({'id': chat.id})


class GenerateReportView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Generate a report for the user"
    )
    def get(self, request, chat_id):
        user = request.user
        chat = User(id=chat_id, name="Эламир", surname="Кадыргалеев", age=20)
        result = analyze_dialogue(chat)
        new_report = GPTReport(user=user, report_data=result)
        new_report.save()

        vocabulary_score = result.get('vocabulary', {}).get('score', 0)
        communication_score = result.get('communication_effectiveness', {}).get('score', 0)
        contextual_score = result.get('contextual_understanding', {}).get('score', 0)

        experience, created = Experience.objects.get_or_create(user=user)
        experience.vocabulary_exp += vocabulary_score * 10
        experience.speaking_exp += communication_score * 10
        experience.grammar_exp += contextual_score * 10
        experience.save()
        return JsonResponse({"report": result})


class ListUserReportsView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Get all GPT reports for the logged-in user"
    )
    def get(self, request):
        reports = GPTReport.objects.filter(user=request.user)
        serializer = GPTReportSerializer(reports, many=True)
        return Response(serializer.data)


class LearningProgramView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, level):
        lessons = Lessons.objects.filter(level=level)
        lessons_serializer = LessonsSerializer(lessons, many=True)

        tasks_done = TaskAnswer.objects.filter(
            task__lesson__level=level,
            user=request.user,
            correct=True
        ).count()
        tasks_total = Tasks.objects.filter(lesson__level=level).count()

        return Response({
            'lessons': lessons_serializer.data,
            'tasks_done': tasks_done,
            'tasks_total': tasks_total
        })


class LessonDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        lesson = Lessons.objects.prefetch_related('tasks').get(id=id)
        serializer = LessonsSerializer(lesson)
        return Response(serializer.data)


class TaskAnswerView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, id):
        task = Tasks.objects.get(id=id)
        provided_answer = request.data.get('answer')
        correct = provided_answer == task.correct_answer

        with transaction.atomic():
            TaskAnswer.objects.create(
                user=request.user,
                task=task,
                answer=provided_answer,
                correct=correct
            )

            if correct:
                experience, created = Experience.objects.get_or_create(user=request.user)
                experience.reading_exp += 200
                experience.grammar_exp += 500
                experience.vocabulary_exp += 200
                experience.save()

        return Response({'correct': correct})


class ReadingListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        readings = Reading.objects.all()
        serializer = ReadingSerializer(readings, many=True)
        return Response(serializer.data)


class ReadingDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        try:
            reading = Reading.objects.prefetch_related('questions').get(id=id)
            serializer = ReadingSerializer(reading)
            return Response(serializer.data)
        except Reading.DoesNotExist:
            return Response({'message': 'Reading not found'}, status=404)


class ReadingAnswerView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        answers_kk = [answer_data.get('answer') for answer_data in request.data.get('answers', [])]
        question_ids = [answer_data.get('id') for answer_data in request.data.get('answers', [])]

        reading_questions = ReadingQuestion.objects.filter(id__in=question_ids).select_related('reading')

        questions_en = {rq.id: rq.question_en for rq in reading_questions}
        readings_texts = {rq.id: rq.reading.text_en for rq in reading_questions}

        questions_en_list = [questions_en.get(id) for id in question_ids]
        readings_texts_list = [readings_texts.get(id) for id in question_ids]

        api_result = check_reading_answers(answers_kk, questions_en_list, readings_texts_list[0])

        try:
            with transaction.atomic():
                experience, created = Experience.objects.get_or_create(user=request.user)
                for i, answer_data in enumerate(request.data.get('answers', [])):
                    question_id = answer_data.get('id')
                    score = api_result['scores'][i]
                    ReadingAnswer.objects.create(
                        user=request.user,
                        reading_question_id=question_id,
                        answer=answers_kk[i],
                        correct=api_result['scores'][i]
                    )

                    if score == 1:
                        experience.reading_exp += 500
                        experience.writing_exp += 300
                        experience.vocabulary_exp += 100
        except Exception as e:
            return Response({'error': 'Failed to save reading answers. ' + str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(api_result)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_audio(request, chat_id):
    audio_file = request.FILES.get('audio_file')
    if not audio_file:
        return JsonResponse({'error': 'No audio file provided'}, status=status.HTTP_400_BAD_REQUEST)

    upload_dir = os.path.join(settings.BASE_DIR, 'media')
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, audio_file.name)
    print("Attempting to save to:", file_path)

    with open(file_path, 'wb+') as destination:
        for chunk in audio_file.chunks():
            destination.write(chunk)

    try:
        chat = Chat.objects.get(id=chat_id)
        user = User(id=chat_id, name="Эламир", surname="Кадыргалеев", age=20)
        response_text = query_api(user, path_to_audio=file_path)
        print(response_text)

        url = "https://7a68-178-91-253-72.ngrok-free.app/synthesize/"
        data = {"text": response_text}
        post_text_to_service.delay(url, data)

        return JsonResponse({'response': response_text})
    except Chat.DoesNotExist:
        return JsonResponse({'error': 'Chat not found'}, status=status.HTTP_404_NOT_FOUND)
    except User.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)