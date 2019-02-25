from django.shortcuts import render,get_object_or_404,redirect
from .models import Board, Topic, Post, Department, Management, Shift,ShiftDetail,ManagementDetail
from accounts.models import User
from .forms import NewTopicForm,PostForm,GroupCreateForm,ShiftDetailForm,ManageDetailForm
from django.contrib.auth.decorators import login_required
import datetime
import calendar
from .forms import ShiftManagementFormSet, ShiftSubmitFormSet
from django.contrib import messages
import numpy as np, pandas as pd
from pulp import *
from ortoolpy import addvars, addbinvars

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
    date_list = range(1,lastday+1) #１から月の最後の日までのリスト
    return render(request,'group_page.html',{'group':group, 'shift_list':shift_list, 'date_list':date_list})

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

@login_required
def shift_detail(request,pk):
    group = get_object_or_404(Department, pk=pk)
    user = request.user
    if group_login_check(user,group) == False:
        messages.error(request, 'グループにログインしてください')
        return redirect('group_login')
    year = datetime.datetime.now().year
    month = datetime.datetime.now().month #現在の年と月を取得
    _, lastday = calendar.monthrange(year,month) #その月の最後の日にちを取得
    obj,created = ShiftDetail.objects.get_or_create(year=year,month=month,department=group,user=user)
    if request.method == 'POST':
        form = ShiftDetailForm(request.POST,instance=obj)
        if form.is_valid():
            form.save()
            shift_list = shift_list_create(user,group)
            date_list = range(1,lastday+1)
            params = {
                'group':group,
                'shift_list':shift_list,
                'date_list':date_list
            }
            return render(request,'group_page.html',params)
        else:
            form = ShiftDetailForm(instance=obj)
            params ={
                'group':group,
                'user': user,
                'form':form,
                'year':year,
                'month':month,
            }
            return render(request, 'shift_detail.html', params)
    else:
        form = ShiftDetailForm(instance=obj)
        params ={
            'group':group,
            'form':form,
            'year':year,
            'month':month,
        }
    return render(request, 'shift_detail.html', params)

def shift_create(request,pk):
    group = get_object_or_404(Department, pk=pk)
    user = request.user
    year = datetime.datetime.now().year
    month = datetime.datetime.now().month #現在の年と月を取得
    _, lastday = calendar.monthrange(year,month) #その月の最後の日にちを取得
    if group_login_check(user,group) == False:
        messages.error(request, 'グループにログインしてください')
        return redirect('group_login')

    shift_list = shift_list_create(user,group)
    date_list = range(0,lastday)
    kari,user_list,m = [],[],[]
    #パートが一つの場合のみなので後で修正
    for count ,_ in enumerate(shift_list[0]):
        m.append(count)
    m.pop(0)
    for i_m in m:
        kari.append(shift_list[0][i_m][1])
        user_list.append(shift_list[0][i_m][0])
    s = pd.DataFrame(kari,index=user_list,columns=date_list).T
    man = Management.objects.filter(year=year,month=month,department=group,part=1).\
    values_list('need',flat=True)
    s['need'] = man
    k = LpProblem()
    N日, N従業員 = s.shape[0], s.shape[1]-1
    L日,L従業員 = list(range(N日)),list(range(N従業員))
    V割当 = pd.DataFrame(np.array(addbinvars(N日, N従業員)),columns=user_list,index=date_list)
    L多め = list(ShiftDetail.objects.filter(year=year,month=month,department=group,degree=0).\
    values_list('user',flat=True))
    L普通 = list(ShiftDetail.objects.filter(year=year,month=month,department=group,degree=1).\
    values_list('user',flat=True))
    L少なめ = list(ShiftDetail.objects.filter(year=year,month=month,department=group,degree=2).\
    values_list('user',flat=True))
    L_big,L_nor,L_sma = [],[],[]
    for i_1 in L多め:
        L_big.append(User.objects.get(id=i_1).username)
    for i_1 in L普通:
        L_nor.append(User.objects.get(id=i_1).username)
    for i_1 in L少なめ:
        L_sma.append(User.objects.get(id=i_1).username)
    man_det = ManagementDetail.objects.get(year=year,month=month,relation=group)

    user_man = []


    C希望不可 = 101
    C必要人数差 = 100
    C勤務日数 = 3
    C3連勤 = 5
    C4連勤 = 20
    #z = addvars(2)
    kk = 0
    s_rev = s[user_list].apply(lambda r: 1-r[user_list],1)
    for (_,r),(_,d) in zip(s_rev.iterrows(),V割当.iterrows()):
        kk += C希望不可 * lpDot(r,d)
    s['V必要人数差'] = addvars(N日)
    k += C必要人数差 * lpSum(s.V必要人数差) + kk
    #+ C勤務日数 * (z[1]-z[0])
    for _,r in V割当[L_big].iteritems():
        k += lpSum(r) >= man_det.min0
        k += lpSum(r) <= man_det.max0
    for _,r in V割当[L_nor].iteritems():
        k += lpSum(r) >= man_det.min1
        k += lpSum(r) <= man_det.max1
    for _,r in V割当[L_sma].iteritems():
        k += lpSum(r) >= man_det.min2
        k += lpSum(r) <= man_det.max2

    for (_,r),(_,d) in zip(s.iterrows(),V割当.iterrows()):
        k += r.V必要人数差 >=  (lpSum(d) - r.need)
        k += r.V必要人数差 >= -(lpSum(d) - r.need)
    for i in L従業員:
        for i in (V割当.values[:-2,i] + V割当.values[1:-1,i] + V割当.values[2:,i]).flat:
            print(i)
            k += i <= 2
    k.solve()
    R結果 = np.vectorize(value)(V割当).astype(int)
    s['結果'] = [''.join(i*j for i,j in zip(r,s.columns)) for r in R結果]
    print(s)
    print('目的関数', value(k.objective))
    print(np.sum(R結果, axis=0))

    return render(request, 'shift_create.html')

def management_detail(request,pk):
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
    obj,created = ManagementDetail.objects.get_or_create(relation=group,year=year,month=month)

    if request.method == 'POST':
        form = ManageDetailForm(request.POST,instance=obj)
        if form.is_valid():
            form.save()
            shift_list = shift_list_create(user,group)
            date_list = range(1,lastday+1)
            params = {
                'group':group,
                'shift_list':shift_list,
                'date_list':date_list
            }
            return render(request,'group_page.html',params)
        else:
            form = ManageDetailForm(instance=obj)
            params ={
                'group':group,
                'form':form,
                'year':year,
                'month':month,
            }
            return render(request, 'management_detail.html', params)
    else:
        form = ManageDetailForm(instance=obj)
        params ={
            'group':group,
            'form':form,
            'year':year,
            'month':month,
        }
    return render(request, 'management_detail.html', params)





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
