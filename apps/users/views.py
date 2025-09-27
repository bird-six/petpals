import json
from urllib.parse import quote
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import check_password
from django.http import JsonResponse
from django.shortcuts import render, redirect
import http.client

from apps.orders.models import Order
from apps.users.models import User, Address
from tools.pet_age import calculate_pet_age


def user_profile(request):
    # 判断是否为AJAX请求（通过请求头或参数）
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    if is_ajax:
        # 返回局部模板（不含header/footer）
        return render(request, 'users/partial/profile_partial.html', {'user': request.user})
    else:
        # 返回完整页面
        return render(request, 'users/user_profile.html', {'user': request.user})

def my_orders(request):
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    # 获取用户所有订单（按创建时间倒序）
    orders = Order.objects.filter(user=request.user).order_by('-created_time')

    for order in orders:
        for item in order.items.all():
            # 计算宠物年龄并添加到订单项对象上
            item.pet_age = calculate_pet_age(item.pet.birth_date)

    if is_ajax:
        # 返回局部模板（不含header/footer）
        return render(request, 'users/partial/my_orders_partial.html', {'user': request.user, 'orders': orders})
    else:
        # 返回完整页面
        return render(request, 'users/my_orders.html', {'orders': orders})


def shopping_cart(request):
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    if is_ajax:
        return render(request, 'users/partial/shopping_cart_partial.html', {'user': request.user})
    else:
        return render(request, 'users/shopping_cart.html')

def addresses(request):
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    addresses = request.user.addresses.all()
    if is_ajax:
        return render(request, 'users/partial/addresses_partial.html', {'user': request.user, 'addresses': addresses})
    else:
        return render(request, 'users/addresses.html', {'addresses': addresses})

def set_default_address(request, address_id):
    if request.method == 'POST':
        try:
            # 查找指定地址
            address = Address.objects.get(id=address_id, user=request.user)
            # 取消其他地址的默认状态
            Address.objects.filter(user=request.user, is_default=True).update(is_default=False)
            # 设置当前地址为默认
            address.is_default = True
            address.save()
            return JsonResponse({'success': True, 'message': '默认地址设置成功'})
        except Address.DoesNotExist:
            return JsonResponse({'success': False, 'message': '地址不存在或不属于当前用户'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    return JsonResponse({'success': False, 'message': '请求方法错误'})

def browsing_history(request):
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    if is_ajax:
        return render(request, 'users/partial/browsing_history_partial.html', {'user': request.user})
    else:
        return render(request, 'users/browsing_history.html')

def my_posts(request):
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    if is_ajax:
        return render(request, 'users/partial/my_posts_partial.html', {'user': request.user})
    else:
        return render(request, 'users/my_posts.html')


def my_favorites(request):
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    if is_ajax:
        return render(request, 'users/partial/my_favorites_partial.html', {'user': request.user})
    else:
        return render(request, 'users/my_favorites.html')

def account_settings(request):
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    if is_ajax:
        return render(request, 'users/partial/account_settings_partial.html', {'user': request.user})
    else:
        return render(request, 'users/account_settings.html')


def user_login(request):
    if request.method == 'POST':
        # 获取表单数据
        email = request.POST.get('email')
        password = request.POST.get('password')
        # 验证用户
        user = User.objects.filter(email=email).first()
        if user and check_password(password, user.password):
            login(request, user)
            return JsonResponse({'success': True, 'redirect': '/', 'message': '登录成功'})
        else:
            return JsonResponse({'success': False, 'message': '邮箱或密码错误'}, status=401)
    return render(request, 'users/login_register.html')


def user_register(request):
    if request.method == 'POST':
        # 获取表单数据
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm-password')
        # 检查邮箱是否已注册
        if User.objects.filter(email=email).exists():
            return JsonResponse({'success': False, 'message': '邮箱已注册'})
        # 检查密码是否为空
        if not password or not confirm_password:
            return JsonResponse({'success': False, 'message': '密码不能为空'})
        # 验证密码是否一致
        if password != confirm_password:
            return JsonResponse({'success': False, 'message': '两次密码不一致'})
        # 是否同意协议
        if not request.POST.get('terms'):
            return JsonResponse({'success': False, 'message': '请同意协议'})

        try:
            # 注册用户
            user = User(email=email)
            user.set_password(password)
            user.save()
            # 登录用户
            login(request, user)
            return JsonResponse({'success': True, 'redirect': '/', 'message': '注册成功！'})
        except Exception as e:
            # 捕获所有异常并返回错误信息
            return JsonResponse({'success': False, 'message': f'注册失败：{str(e)}'})

    # 如果不是POST请求，返回HTML页面
    return render(request, 'users/login_register.html')

def user_logout(request):
    logout(request)
    return redirect('users:user_login')


@login_required
def get_provinces(request):
    """调用第三方api获取所有省份数据"""
    try:
        conn = http.client.HTTPSConnection("hmajax.itheima.net")
        payload = ''
        headers = {}
        conn.request("GET", "/api-s/provincesList", payload, headers)
        res = conn.getresponse()
        data = res.read()
        provinces = json.loads(data.decode("utf-8"))
        return JsonResponse({'success': True, 'provinces': provinces})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})


@login_required
def get_cities(request):
    """根据省份获取城市数据"""
    pname = request.GET.get('pname')
    if not pname:
        return JsonResponse({'success': False, 'message': '省份名称不能为空'})

    try:
        conn = http.client.HTTPSConnection("hmajax.itheima.net")
        payload = ''
        headers = {}
        # 对中文省份名称进行URL编码
        encoded_pname = quote(pname, encoding='utf-8')
        conn.request("GET", f"/api/city?pname={encoded_pname}", payload, headers)
        res = conn.getresponse()
        data = res.read()
        cities = json.loads(data.decode("utf-8"))
        return JsonResponse({'success': True, 'cities': cities})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})


@login_required
def get_districts(request):
    """根据省份和城市获取区县数据"""
    pname = request.GET.get('pname')
    cname = request.GET.get('cname')
    if not pname or not cname:
        return JsonResponse({'success': False, 'message': '省份和城市名称不能为空'})

    try:
        conn = http.client.HTTPSConnection("hmajax.itheima.net")
        payload = ''
        headers = {}
        # 对中文参数进行URL编码
        encoded_pname = quote(pname, encoding='utf-8')
        encoded_cname = quote(cname, encoding='utf-8')
        conn.request("GET", f"/api/area?pname={encoded_pname}&cname={encoded_cname}", payload, headers)
        res = conn.getresponse()
        data = res.read()
        districts = json.loads(data.decode("utf-8"))
        return JsonResponse({'success': True, 'districts': districts})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

@login_required
def add_address(request):
    """添加新地址"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            # 创建地址对象
            address = Address(
                user=request.user,
                recipient_name=data.get('recipient_name'),
                phone_number=data.get('phone_number'),
                province=data.get('province'),
                city=data.get('city'),
                district=data.get('district'),
                detail_address=data.get('address_detail'),
                is_default=data.get('set_default', False)
            )

            # 如果设置为默认地址，取消其他地址的默认状态
            if data.get('set_default', False):
                Address.objects.filter(user=request.user, is_default=True).update(is_default=False)

            address.save()

            return JsonResponse({'success': True, 'message': '地址添加成功'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})

    return JsonResponse({'success': False, 'message': '请求方法错误'})
@login_required
def delete_address(request, address_id):
    """删除地址"""
    if request.method == 'POST':
        try:
            # 查找指定地址并验证所有权
            address = Address.objects.get(id=address_id, user=request.user)
            # 删除地址
            address.delete()
            return JsonResponse({'success': True, 'message': '地址删除成功'})
        except Address.DoesNotExist:
            return JsonResponse({'success': False, 'message': '地址不存在或不属于当前用户'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    return JsonResponse({'success': False, 'message': '请求方法错误'})

@login_required
def get_address(request, address_id):
    """获取地址详情"""
    if request.method == 'GET':
        try:
            # 查找指定地址并验证所有权
            address = Address.objects.get(id=address_id, user=request.user)
            # 构建地址详情数据
            address_data = {
                'id': address.id,
                'recipient_name': address.recipient_name,
                'phone_number': address.phone_number,
                'province': address.province,
                'city': address.city,
                'district': address.district,
                'detail_address': address.detail_address,
                'is_default': address.is_default
            }
            return JsonResponse({'success': True, 'address': address_data})
        except Address.DoesNotExist:
            return JsonResponse({'success': False, 'message': '地址不存在或不属于当前用户'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    return JsonResponse({'success': False, 'message': '请求方法错误'})


@login_required
def edit_address(request, address_id):
    """编辑地址"""
    if request.method == 'POST':
        try:
            # 查找指定地址并验证所有权
            address = Address.objects.get(id=address_id, user=request.user)
            data = json.loads(request.body)

            # 更新地址信息
            address.recipient_name = data.get('recipient_name', address.recipient_name)
            address.phone_number = data.get('phone_number', address.phone_number)
            address.province = data.get('province', address.province)
            address.city = data.get('city', address.city)
            address.district = data.get('district', address.district)
            address.detail_address = data.get('address_detail', address.detail_address)

            # 处理默认地址设置
            set_default = data.get('set_default', False)
            if set_default and not address.is_default:
                # 取消其他地址的默认状态
                Address.objects.filter(user=request.user, is_default=True).update(is_default=False)
                address.is_default = True
            elif not set_default and address.is_default:
                address.is_default = False

            address.save()

            return JsonResponse({'success': True, 'message': '地址更新成功'})
        except Address.DoesNotExist:
            return JsonResponse({'success': False, 'message': '地址不存在或不属于当前用户'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    return JsonResponse({'success': False, 'message': '请求方法错误'})
