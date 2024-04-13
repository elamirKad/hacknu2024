from rest_framework import serializers
from .models import Experience, ReadingQuestion, GrammarQuestion, VocabularyQuestion, ReadingAnswer, GrammarAnswer, VocabularyAnswer


class ExperienceSerializer(serializers.ModelSerializer):
    total_level = serializers.SerializerMethodField()
    total_experience = serializers.ReadOnlyField()

    class Meta:
        model = Experience
        fields = ('reading_exp', 'speaking_exp', 'grammar_exp', 'vocabulary_exp', 'writing_exp', 'total_experience', 'total_level')

    def get_total_level(self, obj):
        level, title = obj.total_level
        return {'level': level, 'title': title}


class ReadingQuestionSerializer(serializers.ModelSerializer):
    solved = serializers.SerializerMethodField()

    class Meta:
        model = ReadingQuestion
        fields = ('id', 'text', 'audio_url', 'question', 'ideal_answer', 'level', 'solved')

    def get_solved(self, obj):
        user = self.context['request'].user
        answer = obj.answers.filter(user=user).first()
        return answer.correct if answer else False


class GrammarQuestionSerializer(serializers.ModelSerializer):
    solved = serializers.SerializerMethodField()

    class Meta:
        model = GrammarQuestion
        fields = ('id', 'question', 'answers', 'correct_answer', 'level', 'solved')

    def get_solved(self, obj):
        user = self.context['request'].user
        answer = obj.user_answers.filter(user=user).first()
        return answer.correct if answer else False


class VocabularyQuestionSerializer(serializers.ModelSerializer):
    solved = serializers.SerializerMethodField()

    class Meta:
        model = VocabularyQuestion
        fields = ('id', 'question', 'answers', 'correct_answer', 'level', 'solved')

    def get_solved(self, obj):
        user = self.context['request'].user
        answer = obj.user_answers.filter(user=user).first()
        return answer.correct if answer else False
