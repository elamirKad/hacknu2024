from django.urls import path
from .views import UserExperienceView, GetQuestionsByLevelView, GetReadingQuestion, GetGrammarQuestion, GetVocabularyQuestion

urlpatterns = [
    path('experience/', UserExperienceView.as_view(), name='user-experience'),
    path('questions/<int:level>/', GetQuestionsByLevelView.as_view(), name='get-questions-by-level'),
    path('questions/reading/<int:pk>/', GetReadingQuestion.as_view(), name='get-reading-question'),
    path('questions/grammar/<int:pk>/', GetGrammarQuestion.as_view(), name='get-grammar-question'),
    path('questions/vocabulary/<int:pk>/', GetVocabularyQuestion.as_view(), name='get-vocabulary-question'),
]
