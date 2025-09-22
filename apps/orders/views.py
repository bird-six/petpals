from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from apps.cart.models import Cart, CartItem
from apps.pets.models import Pet


@login_required  # 确保用户已登录
def orders(request):
    if request.method == 'POST':
        # 1. 获取前端提交的选中商品ID列表
        pet_ids = request.POST.getlist('pet_ids')
        if not pet_ids:
            return redirect('cart:cart')  # 无商品ID则返回购物车

        # 2. 验证商品是否属于当前用户的购物车（防止恶意提交）
        user_cart = Cart.objects.get(user=request.user)
        valid_cart_items = CartItem.objects.filter(
            cart=user_cart,
            pet_id__in=pet_ids  # 只保留用户购物车中存在的商品
        )

        # 3. 计算订单总价
        total_price = sum(item.get_total_price() for item in valid_cart_items)

        # 4. 传递数据到订单模板 - 修改这里，传递CartItem而不是Pet
        return render(request, 'orders/orders.html', {
            'selected_items': valid_cart_items,  # 改为传递CartItem对象
            'total_price': total_price
        })

    # 如果是GET请求（直接访问订单页），返回购物车
    return render(request, 'cart/cart.html')
