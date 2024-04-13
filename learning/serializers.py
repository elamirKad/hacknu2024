from django.urls import reverse
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Experience, ReadingQuestion, GrammarQuestion, VocabularyQuestion, ReadingAnswer, GrammarAnswer, \
    VocabularyAnswer, Lecture, GPTReport


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


class ReadingQuestionSerializer(serializers.ModelSerializer):
    solved = serializers.SerializerMethodField()
    path = serializers.SerializerMethodField()

    class Meta:
        model = ReadingQuestion
        fields = ('id', 'text', 'audio_url', 'question', 'ideal_answer', 'level', 'solved', 'path')

    def get_solved(self, obj):
        user = self.context['request'].user
        answer = ReadingAnswer.objects.filter(user=user, reading_question=obj).first()
        return answer.correct if answer else False

    def get_path(self, obj):
        request = self.context.get('request')
        if request is not None:
            return request.build_absolute_uri(reverse('get-reading-question', kwargs={'pk': obj.pk}))
        return None


class GrammarQuestionSerializer(serializers.ModelSerializer):
    solved = serializers.SerializerMethodField()
    path = serializers.SerializerMethodField()

    class Meta:
        model = GrammarQuestion
        fields = ('id', 'question', 'answers', 'correct_answer', 'level', 'solved', 'path')

    def get_solved(self, obj):
        user = self.context['request'].user
        answer = GrammarAnswer.objects.filter(user=user, grammar_question=obj).first()
        return answer.correct if answer else False

    def get_path(self, obj):
        request = self.context.get('request')
        if request is not None:
            return request.build_absolute_uri(reverse('get-grammar-question', kwargs={'pk': obj.pk}))
        return None


class VocabularyQuestionSerializer(serializers.ModelSerializer):
    solved = serializers.SerializerMethodField()
    path = serializers.SerializerMethodField()

    class Meta:
        model = VocabularyQuestion
        fields = ('id', 'question', 'answers', 'correct_answer', 'level', 'solved', 'path')

    def get_solved(self, obj):
        user = self.context['request'].user
        answer = VocabularyAnswer.objects.filter(user=user, vocabulary_question=obj).first()
        return answer.correct if answer else False

    def get_path(self, obj):
        request = self.context.get('request')
        if request is not None:
            return request.build_absolute_uri(reverse('get-vocabulary-question', kwargs={'pk': obj.pk}))
        return None


class LectureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lecture
        fields = ['id', 'title', 'text', 'level']


class GPTReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = GPTReport
        fields = ['id', 'report_data', 'datetime']
