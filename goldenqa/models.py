from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import datetime

class Question(models.Model):
    TAG_CHOICES = [
        ('daily_life', 'Daily Life'),
        ('sports', 'Sports'),
        ('hobbies', 'Hobbies'),
        ('technology', 'Technology'),
        ('education_career', 'Education and Career'),
        ('health_fitness', 'Health and Fitness'),
        ('travel', 'Travel'),
        ('entertainment', 'Entertainment'),
        ('food_cooking', 'Food and Cooking'),
        ('music_arts', 'Music and Arts'),
        ('books_literature', 'Books and Literature'),
        ('relationships', 'Relationships'),
        ('gaming', 'Gaming'),
        ('science_nature', 'Science and Nature'),
        ('philosophy', 'Philosophy'),
        ('other', 'Other'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    tag = models.CharField(max_length=30, choices=TAG_CHOICES, default='other')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.text

    def was_published_recently(self):
        return self.created_at >= timezone.now() - datetime.timedelta(days=1)

class Answer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, related_name='answers', on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def vote_score(self):
        upvote_count = self.upvote_set.count()
        downvote_count = self.downvote_set.count()
        return upvote_count - downvote_count

    def __str__(self):
        return f"Answer by {self.user.username} on {self.question.text[:30]}"

class Upvote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    answer = models.ForeignKey(Answer, related_name='upvote_set', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} upvoted answer {self.answer.id}"

class Downvote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    answer = models.ForeignKey(Answer, related_name='downvote_set', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} downvoted answer {self.answer.id}"

class QuestionLike(models.Model):
    question = models.ForeignKey(Question, related_name='likes', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('question', 'user')

class QuestionDislike(models.Model):
    question = models.ForeignKey(Question, related_name='dislikes', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('question', 'user')