from django.urls import path
from .views import UserExperienceView, GetQuestionsByLevelView

urlpatterns = [
    path('experience/', UserExperienceView.as_view(), name='user-experience'),
    path('questions/<int:level>/', GetQuestionsByLevelView.as_view(), name='get-questions-by-level'),
]
