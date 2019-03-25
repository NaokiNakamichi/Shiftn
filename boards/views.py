from django.shortcuts import render,get_object_or_404,redirect
from .models import Board, Topic, Post, Department, Management, Shift,ShiftDetail,ManagementDetail,ManagementNeed
from accounts.models import User
from .forms import NewTopicForm,PostForm,GroupCreateForm,ShiftDetailForm,ManageDetailForm
from django.contrib.auth.decorators import login_required
import datetime
import calendar
from .forms import ShiftManagementFormSet, ShiftSubmitFormSet,ManagementNeedFormSet
from django.contrib import messages
import numpy as np, pandas as pd
from pulp import *
from ortoolpy import addvars, addbinvars
import jpholiday
w_list = ['月', '火', '水', '木', '金', '土', '日']

def home(request):
    return render(request, 'home.html')

@login_required
def user_home(request):
    user = request.user
    groups = user.belongs.all()
    return render(request, 'user_home.html',{'groups':groups})

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
            messages.success(request,'グループ作成に成功しました')
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

def current_month_plus():
    year = datetime.datetime.now().year
    month = datetime.datetime.now().month + 1
    if month == 13:
        month = 1
    _, lastday = calendar.monthrange(year,month)
    current_month_plus = [year,month,lastday]
    return current_month_plus

@login_required
def group_page(request,pk):
    group = get_object_or_404(Department, pk=pk)
    user = request.user
    if group_login_check(user,group) == False: #グループにログインしていなければログイン画面へ
        messages.error(request,'グループにログインしてください')
        return redirect('group_login')
    current_month = current_month_plus()
    year,month,lastday = current_month[0],current_month[1],current_month[2]
    if Management.objects.\
    filter(year=year,month=month,department=group).exists() == False: #Managementモデルがまだ存在しなければシフト希望は表示しない
        return render(request,'group_page.html',{'group':group})
    shift_list = shift_list_create(user,group)
    date_list = range(1,lastday+1) #１から月の最後の日までのリスト
    weekday_list = weekday_list_create()
    params ={
            'group':group,
            'shift_list':shift_list,
            'weekday_list':weekday_list,
            'month':month
            }
    return render(request,'group_page.html',params)

def shift_list_create(user,group): # シフトを表示させるためのリストを作成
    current_month = current_month_plus()
    year,month,lastday = current_month[0],current_month[1],current_month[2]
    if Management.objects.filter(year=year,month=month,department=group).exists() == False:
        shift_list = []
        return shift_list
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

def weekday_list_create():
    current_month = current_month_plus()
    year,month,lastday = current_month[0],current_month[1],current_month[2]
    date_list = range(1,lastday+1) #１から月の最後の日までのリスト
    weekday_list = []
    for week_day in date_list:
        w = datetime.datetime(year, month, week_day)
        weekday_list.append((week_day,w_list[datetime.datetime.weekday(w)],\
        jpholiday.is_holiday(datetime.date(year, month, week_day))))
    return weekday_list

@login_required
def management(request,pk):
    group = get_object_or_404(Department, pk=pk)
    user = request.user
    if group_login_check(user,group) == False:
        messages.error(request, 'グループにログインしてください')
        return redirect('group_login')
    if group.created_by != user:
        messages.error(request, '管理者権限がありません')
        return redirect('group_page',pk=pk)
    current_month = current_month_plus()
    year,month,lastday = current_month[0],current_month[1],current_month[2]
    params ={
        'group':group,
        'year':year,
        'month':month,
        'lastday':lastday,
    }
    return render(request, 'group_management.html', params)

@login_required
def management_part(request,pk):
    group = get_object_or_404(Department, pk=pk)
    user = request.user
    weekday_list = weekday_list_create()
    if group_login_check(user,group) == False:
        messages.error(request, 'グループにログインしてください')
        return redirect('group_login')
    if group.created_by != user:
        messages.error(request, '管理者権限がありません')
        return redirect('group_page',pk = pk)
    current_month = current_month_plus()
    year,month,lastday = current_month[0],current_month[1],current_month[2]
    obj = Management.objects.filter(year=year,month=month,department=group)
    if obj.exists() == False: #グループのシフトの設定がなければ1ヶ月分の設定を新しく作成
        date = range(1, lastday+1)
        for i in date:
            Management.objects.create(year=year,month=month,date=i,department=group)

    if request.method == 'POST':
        formset = ShiftManagementFormSet(request.POST)
        if formset.is_valid():
            formset.save()
            params = {
                'group':group,
                'weekday_list':weekday_list,
                'month':month
            }
            return render(request,'group_management.html',params)
        else:
            formset = ShiftManagementFormSet(queryset = obj)
            messages.error(request,'設定に失敗しました')
            params ={
                'group':group,
                'formset':formset,
                'weekday_list':weekday_list,
            }
            return render(request, 'management_part.html', params)
    else:
        formset = ShiftManagementFormSet(queryset = obj)
        params ={
            'group':group,
            'formset':formset,
            'weekday_list':weekday_list,
        }
    return render(request, 'management_part.html', params)

def management_need(request,pk):
    group = get_object_or_404(Department, pk=pk)
    user = request.user
    weekday_list = weekday_list_create()
    shift_list = shift_list_create(user,group)
    if group_login_check(user,group) == False:
        messages.error(request, 'グループにログインしてください')
        return redirect('group_login')
    if group.created_by != user:
        messages.error(request, '管理者権限がありません')
        return redirect('group_page',pk=pk)
    current_month = current_month_plus()
    year,month,lastday = current_month[0],current_month[1],current_month[2]
    obj = Management.objects.filter(year=year,month=month,department=group)
    if obj.exists() == False:
        messages.error(request, '先にパート数を設定してください')
        return redirect('group_page',pk=pk)
    ne = ManagementNeed.objects.filter(year=year,month=month,department=group)
    if ne.exists() == False:
        date = range(1, lastday+1)
        for i_date in date:
            manage = Management.objects.get(year=year,month=month,department=group,date=i_date)
            part_obj = manage.part
            part_num = range(1,part_obj+1)
            for i_part in part_num:
                ManagementNeed.objects.create(year=year,month=month,date=i_date,part=i_part,department=group)
    else:
        for obj_i in obj:
            part_obj = obj_i.part
            part_num = range(1,part_obj+1)
            for i_part in part_num:
                if ManagementNeed.objects.filter(year=year,month=month,department=group,date=obj_i.date,part=i_part).exists() == False:
                    ManagementNeed.objects.create(year=year,month=month,date=obj_i.date,part=i_part,department=group)
        for i_ne in ne:
            if i_ne.part > Management.objects.get(year=year,month=month,department=group,date=i_ne.date).part:
                i_ne.delete()

    obj = ManagementNeed.objects.filter(year=year,month=month,department=group)
    obj = obj.order_by('date')
    if request.method == 'POST':
        formset = ManagementNeedFormSet(request.POST)
        if formset.is_valid():
            formset.save()
            params ={
                'group':group,
                'weekday_list':weekday_list,
                'shift_list':shift_list,
                'month':month
            }
            if ManagementDetail.objects.filter(year=year,month=month,relation=group).exists() == False:
                ManagementDetail.objects.create(year=year,month=month,relation=group)
            return render(request,'group_page.html',params)
        else:
            messages.error(request,'設定に失敗しました')
            formset = ManagementNeedFormSet(queryset = obj)
            params ={
                'group':group,
                'formset':formset,
            }
            return render(request, 'management_need.html', params)
    else:
        formset = ManagementNeedFormSet(queryset = obj)
        params ={
            'group':group,
            'formset':formset,
        }
    return render(request, 'management_need.html', params)

@login_required
def group_login(request):
    user = request.user
    if request.method == 'POST':
        form = GroupCreateForm(request.POST)
        if Department.objects.filter(name = request.POST['name']):
            depa = Department.objects.get(name = request.POST['name'])
            if depa.password == request.POST['password']:
                user.belongs.add(depa)
                messages.success(request,'ログインに成功しました')
                return render(request,'group_page.html',{'group':depa})
        else:
            return redirect('group_login')

    else:
        form = GroupCreateForm()
    return render(request, 'group_login.html', {'form': form})


@login_required
def shift_show(request,pk):
    group = get_object_or_404(Department, pk=pk)
    user = request.user
    if group_login_check(user,group) == False: #グループにログインしていなければログイン画面へ
        messages.error(request,'グループにログインしてください')
        return redirect('group_login')
    current_month = current_month_plus()
    year,month,lastday = current_month[0],current_month[1],current_month[2]
    if Management.objects.\
    filter(year=year,month=month,department=group).exists() == False: #Managementモデルがまだ存在しなければシフト希望は表示しない
        return render(request,'shift_show.html',{'group':group})
    shift_list = shift_list_create(user,group)
    date_list = range(1,lastday+1) #１から月の最後の日までのリスト
    weekday_list = weekday_list_create()
    params ={
            'group':group,
            'shift_list':shift_list,
            'weekday_list':weekday_list,
            'month':month
            }
    return render(request,'shift_show.html',params)


@login_required
def shift_submit(request,pk):
    group = get_object_or_404(Department, pk=pk)
    user = request.user
    weekday_list = weekday_list_create()
    if group_login_check(user,group) == False:
        messages.error(request, 'グループにログインしてください')
        return redirect('group_login')

    current_month = current_month_plus()
    year,month,lastday = current_month[0],current_month[1],current_month[2]
    si = Shift.objects.filter(year=year,month=month,department=group,user=user)
    obj = Management.objects.filter(year=year,month=month,department=group)
    if obj.exists() == False:
        messages.error(request, 'シフト設定を先に行なってください')
        return redirect('group_page',pk=pk)
    if si.exists() == False: #グループのシフトの設定がなければ1ヶ月分の設定を新しく作成
        date = range(1, lastday+1)
        for i_date in date:
            part_obj = Management.objects.get(year=year,month=month,department=group,date=i_date).part
            part_num = range(1,part_obj+1)
            for i_part in part_num:
                Shift.objects.create(year=year,month=month,date=i_date,department=group,user=user,part=i_part)
    else:
        for obj_i in obj:
            part_obj = obj_i.part
            part_num = range(1,part_obj+1)
            for i_part in part_num:
                if Shift.objects.filter(year=year,month=month,department=group,date=obj_i.date,part=i_part,user=user).exists() == False:
                    Shift.objects.create(year=year,month=month,date=obj_i.date,part=i_part,department=group,user=user)
        for i_si in si:
            if i_si.part > Management.objects.get(year=year,month=month,department=group,date=i_si.date).part:
                i_si.delete()
    obj = Shift.objects.filter(year=year,month=month,department=group,user=user)
    obj = obj.order_by('date')
    if request.method == 'POST':
        formset = ShiftSubmitFormSet(request.POST)
        if formset.is_valid():
            formset.save()
            shift_list = shift_list_create(user,group)
            date_list = range(1,lastday+1)
            params = {
                'group':group,
                'shift_list':shift_list,
                'date_list':date_list,
                'weekday_list':weekday_list,
                'month':month
            }
            if ShiftDetail.objects.filter(year=year,month=month,department=group,user=user).exists() == False:
                ShiftDetail.objects.create(year=year,month=month,department=group,user=user)
            return render(request,'group_page.html',params)
        else:
            formset = ShiftSubmitFormSet(queryset = obj)
            params ={
                'group':group,
                'formset':formset,
            }
            return render(request, 'shift_submit.html', params)
    else:
        formset = ShiftSubmitFormSet(queryset = obj)
        params ={
            'group':group,
            'formset':formset,
            'month':month,

        }
    return render(request, 'shift_submit.html', params)

@login_required
def shift_detail(request,pk):
    group = get_object_or_404(Department, pk=pk)
    user = request.user
    if group_login_check(user,group) == False:
        messages.error(request, 'グループにログインしてください')
        return redirect('group_login')
    current_month = current_month_plus()
    year,month,lastday = current_month[0],current_month[1],current_month[2]
    weekday_list = weekday_list_create
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
                'date_list':date_list,
                'weekday_list':weekday_list,
                'month':month,
            }
            return render(request,'group_page.html',params)
        else:
            form = ShiftDetailForm(instance=obj)
            messages.error(request,'設定に失敗しました')
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
    current_month = current_month_plus()
    year,month,lastday = current_month[0],current_month[1],current_month[2]
    weekday_list = weekday_list_create()
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
    for us in user_list:
        us_id = User.objects.get(username=us)
        if Shift.objects.filter(user=us_id,department=group,year=year,month=month)\
        .exists() == False:
            messages.error(request,'出してない人がいます')
            return redirect('group_page',pk=pk)

    s = pd.DataFrame(kari,index=user_list,columns=date_list).T
    man = ManagementNeed.objects.filter(year=year,month=month,department=group,part=1).\
    values_list('need',flat=True)

    s['need'] = man
    shortage = []
    for index,r in s[user_list].iterrows():
        if sum(r) < int(s.at[index,'need']):
            shortage.append(index+1)
    if shortage:
        day = ''
        for i in shortage:
            day += (str(i) + '日')
        messages.error(request,day + 'が人数不足です')
        return redirect('group_page',pk=pk)
    holiday_list,long_list = [],[]
    for day in weekday_list:
        if day[2] == True or day[1] == '土' or day[1] == '日':
            holiday_list.append(day[0]-1)
        if day[2] == True or day[1] == '土':
            long_list.append(day[0]-1)
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
    woman_list,veteran_list =[],[]
    for person in user_list:
        if User.objects.get(username=person).gendar == 1:
            woman_list.append(person)

    for veteran in user_list:
        if User.objects.get(username=veteran).experience == 1:
            veteran_list.append(veteran)
        if User.objects.get(username=veteran).experience == 2:
            veteran_list.append(veteran)
    C希望不可 = 101
    C必要人数差 = 10000
    C勤務日数 = 3
    C連勤 = 5
    C回数ずれ = 10
    C休日 = 3
    Cロング = 3
    C男女 = 5
    C経験者 = 5
    s_rev = s[user_list].apply(lambda r: 1-r[user_list],1)
    for (_,r),(_,d) in zip(s_rev.iterrows(),V割当.iterrows()):
        k += lpDot(r,d) <= 0
    s['V必要人数差'] = addvars(N日)
    s['V男女比'] = addvars(N日)
    s['V経験'] = addvars(N日)
    V連勤 = np.array(addbinvars(N日-2, N従業員))
    Vmax = addvars(N従業員)
    Vmin = addvars(N従業員)
    Vholiday = addvars(N従業員)
    Vlong = addvars(N従業員)
    long = pd.DataFrame(Vlong,index=user_list).T
    holi = pd.DataFrame(Vholiday,index=user_list).T
    max = pd.DataFrame(Vmax,index=user_list).T
    min = pd.DataFrame(Vmin,index=user_list).T
    for name,r in V割当[L_big].iteritems():
        k += lpSum(r) + min.at[0,name] >= man_det.min0
        k += lpSum(r) - max.at[0,name] <= man_det.max0
    for name,r in V割当[L_nor].iteritems():
        k += lpSum(r) + min.at[0,name] >= man_det.min1
        k += lpSum(r) - max.at[0,name] <= man_det.max1
    for name,r in V割当[L_sma].iteritems():
        k += lpSum(r) + min.at[0,name] >= man_det.min2
        k += lpSum(r) - max.at[0,name] <= man_det.max2
    for (_,r),(_,d) in zip(s.iterrows(),V割当.iterrows()):
        k += r.V必要人数差 >=  (lpSum(d) - r.need)
        k += r.V必要人数差 >= -(lpSum(d) - r.need)

    for name,r in V割当.loc[long_list].iteritems():
        k += lpSum(r) + long.at[0,name] >= 1
        k += lpSum(r) - long.at[0,name] <= 2
    for name,r in V割当.loc[holiday_list].iteritems():
        k += lpSum(r) + holi.at[0,name] >= 2
        k += lpSum(r) - holi.at[0,name] <= 4


    for (_,r),(_,d) in zip(s.iterrows(),V割当[woman_list].iterrows()):
        k += (r.V男女比 + lpSum(d)) >= man_det.min_women
    for (_,r),(_,d) in zip(s.iterrows(),V割当[veteran_list].iterrows()):
        k += (r.V経験 + lpSum(d)) >= man_det.min_veteran
    for i in L従業員:
        for n,p in enumerate((V割当.values[:-2,i] + V割当.values[1:-1,i] + V割当.values[2:,i]).flat):
            k += p - V連勤[n][i] <= 2

    k += C必要人数差 * lpSum(s.V必要人数差)\
    + C男女 * lpSum(s.V男女比) \
    + C経験者 * lpSum(s.V経験) \
    + C連勤 * lpSum(V連勤) \
    + C回数ずれ * lpSum(Vmax) \
    + C回数ずれ * lpSum(Vmin)\
    + C休日 * lpSum(Vholiday)\
    + Cロング * lpSum(Vlong)

    k.solve()
    R結果 = np.vectorize(value)(V割当).astype(int)
    R連勤 = np.vectorize(value)(V連勤).astype(int)
    fi = []
    for cou,r in enumerate(R結果):
        fi.append([])
        for i,j in zip(r,s.columns):
            if i*j != '':
                fi[cou].append(i*j)
    print('目的関数', value(k.objective))
    print(R結果)
    print(R連勤)
    show = []
    frequ = []
    for name in user_list:
        user=User.objects.get(username=name).id
        det = ShiftDetail.objects.filter(year=year,month=month,department=group,user=user).exists()
        if det == True:
            det_degree = ShiftDetail.objects.get(year=year,month=month,department=group,user=user).degree
        if det_degree == 0:
            frequ.append('多')
        elif det_degree == 1:
            frequ.append('普')
        else:
            frequ.append('少')
    renkin = []
    for i in np.sum(R連勤,axis=0):
        if i >= 1:
            renkin.append('有')
        else:
            renkin.append('無')
    count = [user_list,frequ,np.sum(R結果, axis=0),\
    np.sum(R結果[holiday_list],axis=0),renkin]
    for r,d in zip(weekday_list,fi):
        show.append([r,d])
    params = {
        'show':show,
        'count':count,

    }
    return render(request, 'shift_create.html',params)

def management_detail(request,pk):
    group = get_object_or_404(Department, pk=pk)
    user = request.user
    weekday_list = weekday_list_create()
    if group_login_check(user,group) == False:
        messages.error(request, 'グループにログインしてください')
        return redirect('group_login')
    if group.created_by != user:
        messages.error(request, '管理者権限がありません')
        return redirect('group_page',pk=pk)
    current_month = current_month_plus()
    year,month,lastday = current_month[0],current_month[1],current_month[2]
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
                'weekday_list':weekday_list,
                'month':month,
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
