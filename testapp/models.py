from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """Extends Django's built-in User — adds role field."""
    ROLE_CHOICES = [
        ('teacher', 'Teacher'),
        ('student', 'Student'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')

    def __str__(self):
        return f"{self.username} ({self.role})"


class Test(models.Model):
    title        = models.CharField(max_length=200)
    created_by   = models.ForeignKey(User, on_delete=models.CASCADE,
                                     related_name='created_tests')
    time_limit   = models.PositiveIntegerField(default=30)   # minutes
    is_published = models.BooleanField(default=False)
    created_at   = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Question(models.Model):
    TYPE_CHOICES = [('mcq', 'MCQ'), ('text', 'Text')]

    test          = models.ForeignKey(Test, on_delete=models.CASCADE,
                                      related_name='questions')
    text          = models.TextField()
    question_type = models.CharField(max_length=5, choices=TYPE_CHOICES)
    marks         = models.PositiveIntegerField(default=1)

    def __str__(self):
        return self.text[:60]


class Option(models.Model):
    question   = models.ForeignKey(Question, on_delete=models.CASCADE,
                                   related_name='options')
    text       = models.CharField(max_length=300)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.text


class Submission(models.Model):
    student      = models.ForeignKey(User, on_delete=models.CASCADE,
                                     related_name='submissions')
    test         = models.ForeignKey(Test, on_delete=models.CASCADE,
                                     related_name='submissions')
    score        = models.FloatField(null=True, blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.username} → {self.test.title}"


class Response(models.Model):
    """One answer to one question within a submission."""
    submission  = models.ForeignKey(Submission, on_delete=models.CASCADE,
                                    related_name='responses')
    question    = models.ForeignKey(Question, on_delete=models.CASCADE)
    chosen_option = models.ForeignKey(Option, on_delete=models.SET_NULL,
                                      null=True, blank=True)  # MCQ
    text_answer   = models.TextField(blank=True)              # Text Q
    marks_awarded = models.FloatField(default=0)