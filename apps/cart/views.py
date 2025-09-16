from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect

from apps.cart.models import Cart, CartItem
from apps.pets.models import Pet


def cart(request):
    return render(request, 'cart/cart.html')

@login_required(login_url='users/login/')
def add_pet_to_cart(request, pet_id):
    pet = get_object_or_404(Pet, id=pet_id)
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_item, item_created = CartItem.objects.get_or_create(
        cart=cart,
        pet=pet,
        defaults={'quantity': 1}
    )

    # 如果购物车中已有该宠物，则数量加1
    if not item_created:
        cart_item.quantity += 1
        cart_item.save()

    # 检查是否为AJAX请求
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': f'{pet.name} 已成功加入购物车！',
            'item_count': cart.get_item_count()
        })
    # 非AJAX请求重定向到购物车页面
    return redirect('cart:cart')