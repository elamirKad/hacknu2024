from django.urls import path
from .views import UserExperienceView, send_text, CreateChatView, GenerateReportView, ListUserReportsView, \
    LearningProgramView, ReadingListView, ReadingDetailView, ReadingAnswerView, LessonDetailView, TaskAnswerView

urlpatterns = [
    path('experience/', UserExperienceView.as_view(), name='user-experience'),
    path('chat/<int:chat_id>/', send_text, name='send-text'),
    path('chat/create/', CreateChatView.as_view(), name='create-chat'),
    path('chat/report/<int:chat_id>/', GenerateReportView.as_view(), name='generate-report'),
    path('chat/reports/', ListUserReportsView.as_view(), name='list-user-reports'),
    path('program/<int:level>/', LearningProgramView.as_view(), name='learning-program'),
    path('lesson/<int:id>/', LessonDetailView.as_view(), name='learning-lesson'),
    path('task/<int:id>/', TaskAnswerView.as_view(), name='learning-task'),
    path('reading/', ReadingListView.as_view(), name='learning-reading'),
    path('reading/<int:id>/', ReadingDetailView.as_view(), name='learning-reading-detail'),
    path('reading/task/', ReadingAnswerView.as_view(), name='learning-reading-answer'),
]
