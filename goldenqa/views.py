from django.shortcuts import render, redirect, get_object_or_404
from .models import Question, Answer, Upvote, Downvote
from .forms import QuestionForm, AnswerForm, SignUpForm
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseForbidden
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.http import JsonResponse, HttpResponseForbidden
from django.db.models import Count, F, IntegerField, ExpressionWrapper

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = SignUpForm()
    return render(request, 'cores/signup.html', {'form': form})

def home(request):
    all_tags = dict(Question.TAG_CHOICES)
    selected_tag = request.GET.get('tag')

    if selected_tag:
        questions = Question.objects.filter(tag=selected_tag).annotate(
            like_count=Count('likes'),
            dislike_count=Count('dislikes')
        ).annotate(
            total_votes=F('like_count') + F('dislike_count')
        ).order_by('-total_votes', '-created_at')
    else:
        questions = None

    login_warning = None
    if request.method == 'POST':
        if not request.user.is_authenticated:
            form = QuestionForm(request.POST)
            login_warning = "You must be logged in to submit a question."
        else:
            form = QuestionForm(request.POST)
            if form.is_valid():
                q = form.save(commit=False)
                q.user = request.user
                q.save()
                return redirect('home')
    else:
        form = QuestionForm()

    return render(request, 'cores/home.html', {
        'questions': questions,
        'form': form,
        'all_tags': all_tags,
        'selected_tag': selected_tag,
        'login_warning': login_warning
    })


def question_detail(request, pk):
    question = get_object_or_404(Question, pk=pk)
    user = request.user

    if not user.is_authenticated:
        return render(request, 'cores/must_login.html')

    #Order
    answers = question.answers.annotate(
        upvote_count=Count('upvote_set'),
        downvote_count=Count('downvote_set')
    ).annotate(
        total_votes=F('upvote_count') + F('downvote_count')
    ).order_by('-total_votes', '-created_at')

    user_upvotes = set()
    user_downvotes = set()

    if user.is_authenticated:
        user_upvotes = set(
            Upvote.objects.filter(user=user, answer__in=answers).values_list('answer_id', flat=True)
        )
        user_downvotes = set(
            Downvote.objects.filter(user=user, answer__in=answers).values_list('answer_id', flat=True)
        )

    if request.method == 'POST':
        form = AnswerForm(request.POST)
        if form.is_valid():
            a = form.save(commit=False)
            a.user = user
            a.question = question
            a.save()
            return redirect('question_detail', pk=pk)
    else:
        form = AnswerForm()

    return render(request, 'cores/question_detail.html', {
        'question': question,
        'answers': answers,
        'form': form,
        'user_upvotes': user_upvotes,
        'user_downvotes': user_downvotes,
    })

@login_required
def upvote_answer(request, answer_id):
    if request.method != 'POST':
        return HttpResponseForbidden()  # Sadece POST kabul et

    answer = get_object_or_404(Answer, id=answer_id)
    user = request.user

    # Eğer daha önce downvote yapmışsa, onu kaldır
    Downvote.objects.filter(answer=answer, user=user).delete()

    # Toggle upvote: varsa kaldır yoksa ekle
    upvote, created = Upvote.objects.get_or_create(answer=answer, user=user)
    if not created:
        upvote.delete()

    # Güncel sayıları döndür
    upvotes_count = Upvote.objects.filter(answer=answer).count()
    downvotes_count = Downvote.objects.filter(answer=answer).count()
    vote_score = upvotes_count - downvotes_count

    return JsonResponse({
        'upvotes_count': upvotes_count,
        'downvotes_count': downvotes_count,
        'vote_score': vote_score,
    })


@login_required
def downvote_answer(request, answer_id):
    if request.method != 'POST':
        return HttpResponseForbidden()

    answer = get_object_or_404(Answer, id=answer_id)
    user = request.user

    # Eğer daha önce upvote yapmışsa kaldır
    Upvote.objects.filter(answer=answer, user=user).delete()

    # Toggle downvote
    downvote, created = Downvote.objects.get_or_create(answer=answer, user=user)
    if not created:
        downvote.delete()

    upvotes_count = Upvote.objects.filter(answer=answer).count()
    downvotes_count = Downvote.objects.filter(answer=answer).count()
    vote_score = upvotes_count - downvotes_count

    return JsonResponse({
        'upvotes_count': upvotes_count,
        'downvotes_count': downvotes_count,
        'vote_score': vote_score,
    })


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'cores/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
@require_POST
def vote_answer(request, answer_id):
    answer = get_object_or_404(Answer, id=answer_id)
    user = request.user
    action = request.POST.get('action')

    if action not in ['upvote', 'downvote']:
        return JsonResponse({'error': 'Invalid action'}, status=400)

    upvote = Upvote.objects.filter(answer=answer, user=user).first()
    downvote = Downvote.objects.filter(answer=answer, user=user).first()

    if action == 'upvote':
        if upvote:
            upvote.delete()  # toggle off
        else:
            if downvote:
                downvote.delete()
            Upvote.objects.create(answer=answer, user=user)
    else:  # downvote
        if downvote:
            downvote.delete()
        else:
            if upvote:
                upvote.delete()
            Downvote.objects.create(answer=answer, user=user)

    upvotes_count = Upvote.objects.filter(answer=answer).count()
    downvotes_count = Downvote.objects.filter(answer=answer).count()
    vote_score = upvotes_count - downvotes_count

    if Upvote.objects.filter(answer=answer, user=user).exists():
        user_vote = 'upvote'
    elif Downvote.objects.filter(answer=answer, user=user).exists():
        user_vote = 'downvote'
    else:
        user_vote = None

    return JsonResponse({
        'score': vote_score,
        'upvotes': upvotes_count,
        'downvotes': downvotes_count,
        'user_vote': user_vote
    })

@login_required
def like_question(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    user = request.user

    # Eğer dislike varsa sil
    QuestionDislike.objects.filter(question=question, user=user).delete()

    like, created = QuestionLike.objects.get_or_create(question=question, user=user)
    if not created:
        like.delete()  # toggle off

    likes_count = QuestionLike.objects.filter(question=question).count()
    dislikes_count = QuestionDislike.objects.filter(question=question).count()

    return JsonResponse({'likes': likes_count, 'dislikes': dislikes_count})

@login_required
def dislike_question(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    user = request.user


    QuestionLike.objects.filter(question=question, user=user).delete()

    dislike, created = QuestionDislike.objects.get_or_create(question=question, user=user)
    if not created:
        dislike.delete()

    likes_count = QuestionLike.objects.filter(question=question).count()
    dislikes_count = QuestionDislike.objects.filter(question=question).count()

    return JsonResponse({'likes': likes_count, 'dislikes': dislikes_count})
