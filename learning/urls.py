from django.urls import path
from .views import UserExperienceView

urlpatterns = [
    path('experience/', UserExperienceView.as_view(), name='user-experience'),
]
