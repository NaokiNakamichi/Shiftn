from django.shortcuts import render,get_object_or_404,redirect
from .models import Board, Topic, Post, Department, Management, Shift
from accounts.models import User
from .forms import NewTopicForm,PostForm,GroupCreateForm
from django.contrib.auth.decorators import login_required
import datetime
import calendar
from .forms import ShiftManagementFormSet, ShiftSubmitFormSet
from django.contrib import messages

def home(request):
    boards = Board.objects.all()
    groups = Department.objects.all()
    return render(request, 'home.html',{'boards':boards,'groups':groups})

@login_required
def group_create(request): #グループの作成（ユーザーとの関連も作っておく）
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
    if group_login_check(user,group) == False: #グループにログインしていなければログイン画面へ
        return redirect('group_login')
    year = datetime.datetime.now().year
    month = datetime.datetime.now().month #現在の年と月を取得
    _, lastday = calendar.monthrange(year,month) #その月の最後の日にちを取得
    if Management.objects.\
    filter(year=year,month=month,department=group).exists() == False: #Managementモデルがまだ存在しなければシフト希望は表示しない
        return render(request,'group_page.html',{'group':group})
    shift_list = shift_list_create(user,group)
<<<<<<< HEAD
    date_list = range(1,lastday+1)
    return render(request,'group_page.html',{'group':group, 'shift_list':shift_list, 'date_list'})
=======
    date_list = range(1,lastday+1) #１から月の最後の日までのリスト
    return render(request,'group_page.html',{'group':group, 'shift_list':shift_list, 'date_list':date_list})
>>>>>>> shift_show

def shift_list_create(user,group): # シフトを表示させるためのリストを作成
    year = datetime.datetime.now().year
    month = datetime.datetime.now().month #現在の年と月を取得
    max_part = max(Management.objects.filter(year=year,month=month,department=group).\
    values_list('part',flat=True))
    part_list = range(1,max_part+1) #max_partで月のパート数の最大を取得、max_listで１から最大パート数のリストを作成
    user_list = User.objects.filter(belongs=group).values_list('id',flat=True) #グループに所属するユーザーのリストを作成
    shift_list = [] #表示させたいシフトのリストをセクション、ユーザー名、シフトの希望の順の深さで配列にする
    for i_part_list in part_list:
        kari_list = []
        kari_list.append(i_part_list) #セクション名を追加
        for count,i_user_list in enumerate(user_list):
            kari_list.append([User.objects.get(id=i_user_list).username]) #ユーザー名を追加
            kari_user = User.objects.get(id=i_user_list) #for文中におけるユーザーのオブジェクトを取得
            kari_list[count+1].append(list(Shift.objects.\
            filter(year=year,month=month,department=group,user=kari_user,part=i_part_list).\
            order_by('date').values_list('hope',flat=True))) # シフトを追加
        shift_list.append(kari_list)
    return shift_list



@login_required
def shift_management(request,pk):
    group = get_object_or_404(Department, pk=pk)
    user = request.user
    if group_login_check(user,group) == False:
        messages.error(request, 'グループにログインしてください')
        return redirect('group_login')
    if group.created_by != user:
        messages.error(request, '管理者権限がありません')
        return render(request,'group_page.html',{'group':group})
    year = datetime.datetime.now().year
    month = datetime.datetime.now().month #現在の年と月を取得
    _, lastday = calendar.monthrange(year,month) #その月の最後の日にちを取得
    obj = Management.objects.filter(year=year,month=month,department=group)
    if obj.exists() == False: #グループのシフトの設定がなければ1ヶ月分の設定を新しく作成
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

@login_required
def shift_submit(request,pk):
    group = get_object_or_404(Department, pk=pk)
    user = request.user
    if group_login_check(user,group) == False:
        messages.error(request, 'グループにログインしてください')
        return redirect('group_login')

    year = datetime.datetime.now().year
    month = datetime.datetime.now().month #現在の年と月を取得
    _, lastday = calendar.monthrange(year,month) #その月の最後の日にちを取得
    obj = Shift.objects.filter(year=year,month=month,department=group,user=user)
    if Management.objects.\
    filter(year=year,month=month,department=group).exists() == False:
        messages.error(request, 'シフト設定を先に行なってください')
        return render(request,'group_page.html',{'group':group})
    if obj.exists() == False: #グループのシフトの設定がなければ1ヶ月分の設定を新しく作成
        date = range(1, lastday+1)
        for i_date in date:
            part_obj = Management.objects.get(year=year,month=month,department=group,date=i_date).part
            part_num = range(1,part_obj+1)
            for i_part in part_num:
                Shift.objects.create(year=year,month=month,date=i_date,department=group,user=user,part=i_part)

    if request.method == 'POST':
        formset = ShiftSubmitFormSet(request.POST)
        if formset.is_valid():
            formset.save()
            shift_list = shift_list_create(user,group)
            date_list = range(1,lastday+1)
            params = {
                'group':group,
                'shift_list':shift_list,
                'date_list':date_list
            }
            return render(request,'group_page.html',params)
        else:
            formset = ShiftSubmitFormSet(queryset = obj)
            params ={
                'group':group,
                'formset':formset,
                'year':year,
                'month':month,
                'lastday':lastday,
            }
            return render(request, 'shift_submit.html', params)
    else:
        formset = ShiftSubmitFormSet(queryset = obj)
        params ={
            'group':group,
            'formset':formset,
            'year':year,
            'month':month,
            'lastday':lastday,
        }
    return render(request, 'shift_submit.html', params)





#ここからは使わない





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
