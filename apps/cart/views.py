import json
from datetime import date
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from apps.cart.models import Cart, CartItem
from apps.pets.models import Pet

def calculate_pet_age(birth_date):
    """计算宠物的年龄，返回格式化的年龄字符串"""
    today = date.today()
    # 计算年差
    years = today.year - birth_date.year
    # 计算月差，如果当前月份小于出生月份，则年减1
    months = today.month - birth_date.month
    if months < 0:
        years -= 1
        months += 12
    # 如果宠物还不到1岁，只显示月份
    if years == 0:
        return f"{months}个月"
    # 如果有月份差，同时显示年和月
    elif months > 0:
        return f"{years}岁{months}个月"
    # 否则只显示年
    else:
        return f"{years}岁"



def cart(request):
    if not request.user.is_authenticated:
        return redirect('users:user_login')
    cart_items = CartItem.objects.filter(cart__user=request.user)
    total_price = 0
    for item in cart_items:
        item.pet.age = calculate_pet_age(item.pet.birth_date)
        total_price += item.pet.price * item.quantity
    return render(request, 'cart/cart.html', {'cart_items': cart_items, 'total_price': total_price})


def add_pet_to_cart(request, pet_id):
    # 检查用户是否登录
    if not request.user.is_authenticated:
        return JsonResponse({
            'success': False,
            'message': '请先登录！',
            'login_required': True
        }, status=401)

    if request.method == 'POST':
        pet = get_object_or_404(Pet, id=pet_id)
        cart, created = Cart.objects.get_or_create(user_id=request.user.id)
        # 检查宠物是否已在购物车中
        if CartItem.objects.filter(cart=cart, pet=pet).exists():
            return JsonResponse({
                'success': False,
                'message': f'{pet.name} 已经在您的购物车中了！',
                'item_count': cart.get_item_count()
            })

        # 创建新的购物车项，数量默认为1
        CartItem.objects.create(cart=cart, pet=pet, quantity=1)
        return JsonResponse({
            'success': True,
            'message': f'{pet.name} 已成功加入购物车！',
            'item_count': cart.get_item_count()
        })

    # 如果不是POST请求，返回错误
    return JsonResponse({
        'success': False,
        'message': '请求方法错误！'
    }, status=405)


def delete_pet_to_cart(request, pet_id):
    # 检查用户是否登录
    if not request.user.is_authenticated:
        return JsonResponse({
            'success': False,
            'message': '请先登录！',
            'login_required': True
        }, status=401)

    if request.method == 'POST':
        pet = get_object_or_404(Pet, id=pet_id)
        cart = get_object_or_404(Cart, user=request.user)

        # 查找要删除的购物车项
        cart_item = CartItem.objects.filter(cart=cart, pet=pet).first()
        if cart_item:
            cart_item.delete()
            return JsonResponse({
                'success': True,
                'message': f'{pet.name} 已从购物车移除',
                'item_count': cart.get_item_count()
            })

        return JsonResponse({
            'success': False,
            'message': '该商品不在您的购物车中'
        })

    # 如果不是POST请求，返回错误
    return JsonResponse({
        'success': False,
        'message': '请求方法错误！'
    }, status=405)

def delete_selected_pets(request):
    if not request.user.is_authenticated:
        return JsonResponse({
            'success': False,
            'message': '请先登录！',
            'login_required': True
        }, status=401)

    if request.method == 'POST':
        try:
            # 获取选中的宠物ID列表
            data = json.loads(request.body)
            pet_ids = data.get('pet_ids', [])

            if not pet_ids:
                return JsonResponse({
                    'success': False,
                    'message': '请选择要删除的商品'
                })

            cart = get_object_or_404(Cart, user=request.user)

            # 删除选中的购物车项
            deleted_items = CartItem.objects.filter(cart=cart, pet_id__in=pet_ids)
            deleted_count = deleted_items.count()
            deleted_items.delete()

            return JsonResponse({
                'success': True,
                'message': f'成功删除 {deleted_count} 件商品',
                'item_count': cart.get_item_count(),
                'total_price': cart.get_total_price()
            })
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'message': '请求数据格式错误'
            }, status=400)

    # 如果不是POST请求，返回错误
    return JsonResponse({
        'success': False,
        'message': '请求方法错误！'
    }, status=405)
