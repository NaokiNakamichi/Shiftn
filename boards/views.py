from django.shortcuts import render,get_object_or_404,redirect
from .models import Board, Topic, Post, Department
from accounts.models import User
from .forms import NewTopicForm,PostForm,GroupCreateForm
from django.contrib.auth.decorators import login_required
# Create your views here.
def home(request):
    boards = Board.objects.all()
    groups = Department.objects.all()
    return render(request, 'home.html',{'boards':boards,'groups':groups})

@login_required
def group_create(request):
    user = request.user
    if request.method == 'POST':
        form = GroupCreateForm(request.POST)
        if form.is_valid():
            group = form.save()
            group.created_by = request.user
            group.save()
            user.belongs.add(group)
            return redirect('home')
    else:
        form = GroupCreateForm()
    return render(request, 'group_create.html', {'form': form})

@login_required
def group_page(request,pk):
    group = get_object_or_404(Department, pk=pk)
    user = request.user
    for i in user.belongs.all():
        print(i)
        print(group)
        if group == i:
            return render(request,'group_page.html',{'group':group})
    return redirect('group_login')
    
@login_required
def group_login(request):
    user = request.user
    if request.method == 'POST':
        form = GroupCreateForm(request.POST)
        if Department.objects.filter(name = request.POST['name']):
            depa = Department.objects.get(name = request.POST['name'])
            if depa.password == request.POST['password']:
                user.belongs.add(depa)
                return render(request,'group_page.html',{'group':depa})
        else:
            return redirect('group_login')

    else:
        form = GroupCreateForm()
    return render(request, 'group_login.html', {'form': form})


def board_topics(request,pk):
    board = get_object_or_404(Board, pk=pk)
    return render(request,'topics.html',{'board':board})

def topic_posts(request, pk, topic_pk):
    topic = get_object_or_404(Topic, board__pk=pk, pk=topic_pk)
    return render(request, 'topic_posts.html', {'topic': topic})

@login_required
def reply_topic(request, pk, topic_pk):
    topic = get_object_or_404(Topic, board__pk=pk, pk=topic_pk)
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.topic = topic
            post.created_by = request.user
            post.save()
            return redirect('topic_posts', pk=pk, topic_pk=topic_pk)
    else:
        form = PostForm()
    return render(request, 'reply_topic.html', {'topic': topic, 'form': form})

@login_required
def new_topic(request, pk):
    board = get_object_or_404(Board, pk=pk)
    user = request.user # TODO: get the currently logged in user
    if request.method == 'POST':
        form = NewTopicForm(request.POST)
        if form.is_valid():
            topic = form.save(commit=False)
            topic.board = board
            topic.starter = request.user  # <- here
            topic.save()
            post = Post.objects.create(
                message=form.cleaned_data.get('message'),
                topic=topic,
                created_by=request.user
            )
            return redirect('topic_posts', pk=pk, topic_pk=topic.pk)
    else:
        form = NewTopicForm()
    return render(request, 'new_topic.html', {'board': board, 'form': form})
