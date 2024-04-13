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
        return experience // 1000

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


class ReadingQuestion(models.Model):
    text = models.TextField()
    audio_url = models.URLField(blank=True, null=True)
    question = models.TextField()
    ideal_answer = models.TextField()
    level = models.IntegerField(choices=((1, 'Level 1'), (2, 'Level 2'), (3, 'Level 3')))


class GrammarQuestion(models.Model):
    question = models.TextField()
    answers = models.JSONField()
    correct_answer = models.CharField(max_length=255)
    level = models.IntegerField(choices=((1, 'Level 1'), (2, 'Level 2'), (3, 'Level 3')))


class VocabularyQuestion(models.Model):
    question = models.TextField()
    answers = models.JSONField()
    correct_answer = models.CharField(max_length=255)
    level = models.IntegerField(choices=((1, 'Level 1'), (2, 'Level 2'), (3, 'Level 3')))


class GPTReport(models.Model):
    comment = models.TextField()
    reading_exp = models.IntegerField(default=0)
    speaking_exp = models.IntegerField(default=0)
    grammar_exp = models.IntegerField(default=0)
    vocabulary_exp = models.IntegerField(default=0)
    writing_exp = models.IntegerField(default=0)

    def __str__(self):
        return f"Report {self.id} - Comment: {self.comment[:50]}..."


class ReadingAnswer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    reading_question = models.ForeignKey(ReadingQuestion, related_name='answers', on_delete=models.CASCADE, null=True)
    user_answer = models.TextField()
    gpt_report = models.ForeignKey(GPTReport, on_delete=models.CASCADE)
    correct = models.BooleanField()

    def __str__(self):
        return f"Reading Answer {self.id} - {'Correct' if self.correct else 'Incorrect'}"


class GrammarAnswer(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    grammar_question = models.ForeignKey(GrammarQuestion, related_name='user_answers', null=True, on_delete=models.CASCADE)
    user_answer = models.TextField()
    correct = models.BooleanField()

    def __str__(self):
        return f"Grammar Answer {self.id} - {'Correct' if self.correct else 'Incorrect'}"


class VocabularyAnswer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    vocabulary_question = models.ForeignKey(VocabularyQuestion, related_name='user_answers', on_delete=models.CASCADE, null=True)
    user_answer = models.TextField()
    correct = models.BooleanField()

    def __str__(self):
        return f"Vocabulary Answer {self.id} - {'Correct' if self.correct else 'Incorrect'}"


class SpeakingPractice(models.Model):
    history = models.TextField()
    gpt_report = models.ForeignKey('GPTReport', on_delete=models.CASCADE, related_name='speaking_practices')

    def __str__(self):
        return f"Speaking Practice {self.id}"


class WritingPractice(models.Model):
    history = models.TextField()
    gpt_report = models.ForeignKey('GPTReport', on_delete=models.CASCADE, related_name='writing_practices')

    def __str__(self):
        return f"Writing Practice {self.id}"


class Lecture(models.Model):
    title = models.CharField(max_length=255)
    text = models.TextField()
    level = models.IntegerField(choices=((1, 'Level 1'), (2, 'Level 2'), (3, 'Level 3')))

    def __str__(self):
        return f"{self.title} ({self.level})"
