from django.urls import path
from .views import UserExperienceView, send_text, CreateChatView, GenerateReportView, ListUserReportsView, \
    LearningProgramView, ReadingListView, ReadingDetailView, ReadingAnswerView

urlpatterns = [
    path('experience/', UserExperienceView.as_view(), name='user-experience'),
    path('chat/<int:chat_id>/', send_text, name='send-text'),
    path('chat/create/', CreateChatView.as_view(), name='create-chat'),
    path('chat/report/<int:chat_id>/', GenerateReportView.as_view(), name='generate-report'),
    path('chat/reports/', ListUserReportsView.as_view(), name='list-user-reports'),
    path('program/<int:level>/', LearningProgramView.as_view(), name='learning-program'),
    path('learning/reading/', ReadingListView.as_view(), name='learning-reading'),
    path('learning/reading/<int:id>/', ReadingDetailView.as_view(), name='learning-reading-detail'),
    path('learning/reading/task/<int:id>/', ReadingAnswerView.as_view(), name='learning-reading-answer'),
]
