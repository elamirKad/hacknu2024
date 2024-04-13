from django.contrib import admin
from django.utils.html import format_html
from .models import Experience, ReadingQuestion, GrammarQuestion, VocabularyQuestion, ReadingAnswer, GrammarAnswer, \
    VocabularyAnswer, GPTReport, SpeakingPractice, WritingPractice, Lecture, Chat


@admin.register(Experience)
class ExperienceAdmin(admin.ModelAdmin):
    list_display = ('user', 'reading_exp', 'speaking_exp', 'grammar_exp', 'vocabulary_exp', 'writing_exp', 'display_total_experience', 'display_total_level')
    search_fields = ('user__username',)
    list_filter = ('user__username',)

    def display_total_experience(self, obj):
        return obj.total_experience
    display_total_experience.short_description = 'Total Experience'

    def display_total_level(self, obj):
        level, title = obj.total_level
        return format_html('<b>{}</b> - {}', level, title)
    display_total_level.short_description = 'Total Level'

    fieldsets = (
        (None, {
            'fields': ('user', 'reading_exp', 'speaking_exp', 'grammar_exp', 'vocabulary_exp', 'writing_exp')
        }),
        ('Levels', {
            'fields': (),
            'description': 'The following sections are computed based on the experience values above.'
        }),
        ('Computed Levels', {
            'fields': ('display_total_experience', 'display_total_level'),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ('display_total_experience', 'display_total_level')

    def get_readonly_fields(self, request, obj=None):
        if not request.user.has_perm('learning.change_experience'):
            return self.readonly_fields + ('reading_exp', 'speaking_exp', 'grammar_exp', 'vocabulary_exp', 'writing_exp')
        return self.readonly_fields

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_add_permission(self, request):
        return request.user.is_superuser


admin.site.register(ReadingQuestion)
admin.site.register(GrammarQuestion)
admin.site.register(VocabularyQuestion)
admin.site.register(ReadingAnswer)
admin.site.register(GrammarAnswer)
admin.site.register(VocabularyAnswer)
admin.site.register(GPTReport)
admin.site.register(SpeakingPractice)
admin.site.register(WritingPractice)
admin.site.register(Lecture)
admin.site.register(Chat)
