from django import forms
from .models import User, Question, Answer
from django.contrib.auth.forms import UserCreationForm

class SignUpForm(UserCreationForm):
    username = forms.CharField(max_length=20)

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']

from .models import Question, Answer

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['text', 'tag']

class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ['content']
