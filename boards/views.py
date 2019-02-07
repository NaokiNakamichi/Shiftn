from django.shortcuts import render,get_object_or_404,redirect
from .models import Board, Topic, Post, Department, Management
from accounts.models import User
from .forms import NewTopicForm,PostForm,GroupCreateForm
from django.contrib.auth.decorators import login_required
import datetime
import calendar
from .forms import ShiftManagementFormSet
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

def group_login_check(user,group):
    for i in user.belongs.all(): # ユーザーと関係のあるグループ全て
        if group == i: #現在のグループと合致すれば許可
            return True
        else:
            pass
    return False

@login_required
def group_page(request,pk):
    group = get_object_or_404(Department, pk=pk)
    user = request.user
    if group_login_check(user,group) == True:
        return render(request,'group_page.html',{'group':group})
    else:
        return redirect('group_login')


@login_required
def shift_management(request,pk):
    group = get_object_or_404(Department, pk=pk)
    user = request.user
    if group_login_check(user,group) == True:
        year = datetime.datetime.now().year
        month = datetime.datetime.now().month #現在の年と月を取得
        _, lastday = calendar.monthrange(year,month) #その月の最後の日にちを取得
        obj = Management.objects.filter(year=year,month=month,department=group)
        if obj.exists(): #グループのシフトの設定がすでにあればパス
            pass
        else: #なければ1ヶ月分の設定を新しく作成
            date = range(1, lastday+1)
            for i in date:
                Management.objects.create(year=year,month=month,date=i,department=group)
        if request.method == 'POST':
            formset = ShiftManagementFormSet(request.POST)
            if formset.is_valid():
                formset.save()
                return render(request,'group_page.html',{'group':group})
            else:
                formset = ShiftManagementFormSet(queryset = obj)
                params ={
                    'group':group,
                    'formset':formset,
                    'year':year,
                    'month':month,
                    'lastday':lastday,
                }
                return render(request, 'group_management.html', params)
        else:
            formset = ShiftManagementFormSet(queryset = obj)
            params ={
                'group':group,
                'formset':formset,
                'year':year,
                'month':month,
                'lastday':lastday,
            }
        return render(request, 'group_management.html', params)
    else:
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
'''
@login_required
def shift_submit(request):

    year = datetime.datetime.now().year
    month = 9
    #month = datetime.datetime.now().month
    _, lastday = calendar.monthrange(year,month)
    obj = Kanri.objects.filter(year=year,month=month)
    if obj.exists():
        pass
    else:
        date = range(1, lastday+1)
        for i in date:
            Kanri.objects.create(year=year,month=month,date=i)
    formset = KanriFormSet(queryset = obj)
    if (request.method == 'POST'):
        formset = KanriFormSet(request.POST)
        if formset.is_valid():
            formset.save()
            return redirect(to='/hello')

    params ={
        'title':'Hello',
        'formset':formset,
        'year':year,
        'month':month,
        'lastday':lastday,
    }

    return render(request, 'hello/create.html', params)
'''

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
