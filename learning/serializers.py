from django.urls import reverse
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Experience, ReadingQuestion, GPTReport, Lessons, Tasks, TaskAnswer, Reading, ReadingAnswer


class UserSerializerForStats(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email')


class ExperienceSerializer(serializers.ModelSerializer):
    total_level = serializers.SerializerMethodField()
    total_experience = serializers.ReadOnlyField()
    user_data = UserSerializerForStats(source='user', read_only=True)

    class Meta:
        model = Experience
        fields = ('user_data', 'reading_exp', 'speaking_exp', 'grammar_exp', 'vocabulary_exp', 'writing_exp', 'total_experience', 'total_level')

    def get_total_level(self, obj):
        level, title = obj.total_level
        return {'level': level, 'title': title}


class GPTReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = GPTReport
        fields = ['id', 'report_data', 'datetime']


class TasksSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tasks
        fields = ['id', 'lesson', 'question', 'answers', 'correct_answer']


class LessonsSerializer(serializers.ModelSerializer):
    tasks = TasksSerializer(many=True, read_only=True)

    class Meta:
        model = Lessons
        fields = ['id', 'level', 'markdown', 'tasks']


class TaskAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskAnswer
        fields = ['id', 'user', 'task', 'answer', 'correct']


class ReadingQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReadingQuestion
        fields = ['id', 'question_en', 'question_kz']


class ReadingSerializer(serializers.ModelSerializer):
    questions = ReadingQuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Reading
        fields = ['id', 'text_en', 'text_kz', 'title', 'description', 'level', 'questions']


class ReadingAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReadingAnswer
        fields = ['id', 'user', 'reading_question', 'answer', 'correct']
