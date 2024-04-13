from rest_framework import serializers
from .models import Experience


class ExperienceSerializer(serializers.ModelSerializer):
    total_level = serializers.SerializerMethodField()
    total_experience = serializers.ReadOnlyField()

    class Meta:
        model = Experience
        fields = ('reading_exp', 'speaking_exp', 'grammar_exp', 'total_experience', 'total_level')

    def get_total_level(self, obj):
        level, title = obj.total_level
        return {'level': level, 'title': title}
