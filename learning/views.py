from django.http import JsonResponse
from drf_yasg import openapi
from drf_yasg.openapi import Schema, TYPE_OBJECT, TYPE_INTEGER, TYPE_BOOLEAN, TYPE_STRING
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import permission_classes, api_view
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Experience, ReadingQuestion, Chat, GPTReport, Lessons, TaskAnswer, Tasks, Reading, ReadingAnswer
from .open import User, query_api, analyze_dialogue
from .serializers import ExperienceSerializer, GPTReportSerializer, LessonsSerializer, TasksSerializer, \
    ReadingSerializer, ReadingQuestionSerializer


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
        tasks = Tasks.objects.filter(lesson__id=id)
        serializer = TasksSerializer(tasks, many=True)
        return Response(serializer.data)


class TaskAnswerView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, id):
        task = Tasks.objects.get(id=id)
        provided_answer = request.data.get('answer')
        correct = provided_answer == task.correct_answer

        TaskAnswer.objects.create(
            user=request.user,
            task=task,
            answer=provided_answer,
            correct=correct
        )

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
        questions = ReadingQuestion.objects.filter(reading__id=id)
        serializer = ReadingQuestionSerializer(questions, many=True)
        return Response(serializer.data)


class ReadingAnswerView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, id):
        try:
            reading_question = ReadingQuestion.objects.get(id=id)
            provided_answer = request.data.get('answer')
            correct = (provided_answer == reading_question.ideal_answer)

            ReadingAnswer.objects.create(
                user=request.user,
                reading_question=reading_question,
                answer=provided_answer,
                correct=correct
            )

            return Response({'correct': correct})
        except ReadingQuestion.DoesNotExist:
            return Response({'error': 'Reading question not found.'}, status=status.HTTP_404_NOT_FOUND)
