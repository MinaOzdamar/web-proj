from django.contrib import admin
from django.urls import path
from django.shortcuts import redirect
from django.contrib.auth.views import LoginView, LogoutView
from goldenqa import views  # Import views from your goldenqa app

urlpatterns = [
    path('', lambda request: redirect('login/')),
    path('admin/', admin.site.urls),
    path('signup/', views.signup, name='signup'),
    path('login/', LoginView.as_view(template_name='cores/login.html'), name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('question/<int:pk>/', views.question_detail, name='question_detail'),
    path('home/', views.home, name='home'),
    path('answer/<int:answer_id>/upvote/', views.upvote_answer, name='upvote_answer'),
    path('answer/<int:answer_id>/downvote/', views.downvote_answer, name='downvote_answer'),
    path('vote-answer/<int:answer_id>/', views.vote_answer, name='vote_answer'),
    path('questions/<int:question_id>/like/', views.like_question, name='like_question'),
    path('questions/<int:question_id>/dislike/', views.dislike_question, name='dislike_question'),
    path('questions/', views.question_page, name='question_page'),

]

