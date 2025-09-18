from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import check_password
from django.http import JsonResponse
from django.shortcuts import render, redirect

from apps.users.models import User

@login_required(login_url='users:user_login')
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

    if is_ajax:
        # 返回局部模板（不含header/footer）
        return render(request, 'users/partial/my_orders_partial.html', {'user': request.user})
    else:
        # 返回完整页面
        return render(request, 'users/my_orders.html')


def shopping_cart(request):
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    if is_ajax:
        return render(request, 'users/partial/shopping_cart_partial.html', {'user': request.user})
    else:
        return render(request, 'users/shopping_cart.html')

def addresses(request):
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    if is_ajax:
        return render(request, 'users/partial/addresses_partial.html', {'user': request.user})
    else:
        return render(request, 'users/addresses.html')

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
            return JsonResponse({'message': '登录成功'}, status=200)
        else:
            return JsonResponse({'error': '密码错误'}, status=401)
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
            user = User(email=email, password=password)
            user.save()  # save方法会自动哈希密码
            # 登录用户
            login(request, user)
            return JsonResponse({'success': True, 'redirect': '/', 'message': '注册成功！'})
        except Exception as e:
            # 捕获所有异常并返回错误信息
            return JsonResponse({'success': False, 'message': f'注册失败：{str(e)}'})

    # 如果不是POST请求，返回HTML页面
    return render(request, 'users/login_register.html')
