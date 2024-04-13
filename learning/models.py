from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.contrib.auth.models import User


class Experience(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='experience')
    reading_exp = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(10000)])
    speaking_exp = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(10000)])
    grammar_exp = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(10000)])
    vocabulary_exp = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(10000)])
    writing_exp = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(10000)])

    LEVEL_TITLES = [
        'Жауынгер',  # Level 0
        'Сарбаз',  # Level 1
        'Шаруа',  # Level 2
        'Бай',  # Level 3
        'Ауылбасы',  # Level 4
        'Аксакал',  # Level 5
        'Рубасы',  # Level 6
        'Би',  # Level 7
        'Султан',  # Level 8
        'Хан'  # Level 9
    ]

    def calculate_level(self, experience):
        """Calculate level based on experience."""
        return experience // 3000

    def get_level_title(self, level):
        """Get the title corresponding to the level."""
        if level < len(self.LEVEL_TITLES):
            return self.LEVEL_TITLES[level]
        return "Unknown Level"

    @property
    def total_level(self):
        """Calculate the total level based on all experience."""
        lvl = self.calculate_level(self.total_experience)
        return lvl, self.get_level_title(lvl)

    @property
    def total_experience(self):
        """Calculate the total experience from all categories."""
        return self.reading_exp + self.speaking_exp + self.grammar_exp + self.vocabulary_exp + self.writing_exp

    def __str__(self):
        return f'{self.user.username}'
