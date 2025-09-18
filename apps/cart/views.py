from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from apps.cart.models import Cart, CartItem
from apps.pets.models import Pet


def cart(request):
    return render(request, 'cart/cart.html')


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
        cart, created = Cart.objects.get_or_create(user=request.user)
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