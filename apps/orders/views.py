import json
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from apps.cart.models import Cart, CartItem
from apps.orders.models import Order, OrderItem
from apps.pets.models import Pet
from apps.users.models import Address


@login_required  # 确保用户已登录
def orders(request):
    if request.method == 'POST':
        # 获取用户地址
        user_addresses = Address.objects.filter(user=request.user)
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

        # 4. 传递数据到订单模板 - 传递CartItem
        return render(request, 'orders/orders.html', {
            'selected_items': valid_cart_items,
            'total_price': total_price,
            'user_addresses': user_addresses
        })

    # 如果是GET请求（直接访问订单页），返回购物车
    return render(request, 'cart/cart.html', )


@login_required
def order_submit(request):
    if request.method == 'POST':
        try:
            # 1. 解析JSON数据
            data = json.loads(request.body)

            # 2. 验证必要字段
            if not data.get('address_id'):
                return JsonResponse({
                    'success': False,
                    'message': '请选择收货地址'
                })

            if not data.get('items') or not isinstance(data.get('items'), list):
                return JsonResponse({
                    'success': False,
                    'message': '订单中没有商品'
                })

            # 3. 开始事务处理
            with transaction.atomic():
                # 4. 创建订单主表记录
                # 验证地址ID是有效的数字
                try:
                    address_id = int(data['address_id'])
                except ValueError:
                    return JsonResponse({
                        'success': False,
                        'message': '无效的地址ID'
                    })

                address = get_object_or_404(Address, id=address_id, user=request.user)

                # 验证地址中的收货人信息
                if not address.recipient_name:
                    return JsonResponse({
                        'success': False,
                        'message': '请填写收货人姓名'
                    })

                if not address.phone_number:
                    return JsonResponse({
                        'success': False,
                        'message': '请填写手机号码'
                    })

                order = Order.objects.create(
                    user=request.user,
                    address=address,
                    total_amount=0,
                    status='pending_payment',
                    remark=data.get('remarks', ''),
                    payment_method=data['payment_method']
                )

                # 5. 计算订单总价并创建订单项
                total_price = 0
                for item_data in data['items']:
                    # 验证商品项数据
                    if 'pet_id' not in item_data or 'quantity' not in item_data:
                        return JsonResponse({
                            'success': False,
                            'message': '商品数据格式错误'
                        })

                    # 验证宠物ID是有效的数字
                    try:
                        pet_id = int(item_data['pet_id'])
                    except ValueError:
                        return JsonResponse({
                            'success': False,
                            'message': '无效的商品ID'
                        })

                    # 获取商品并验证
                    pet = get_object_or_404(Pet, id=pet_id)
                    quantity = int(item_data['quantity'])

                    if quantity <= 0:
                        return JsonResponse({
                            'success': False,
                            'message': f'商品"{pet.name}"数量无效'
                        })

                    # 计算单项总价并累加
                    item_total = pet.price * quantity
                    total_price += item_total

                    # 创建订单项
                    OrderItem.objects.create(
                        order=order,
                        pet=pet,
                        price=pet.price,  # 记录下单时的价格
                        count=quantity,
                        total_price=item_total
                    )

                    # 6. 从购物车中移除已购买的商品
                    user_cart = Cart.objects.get(user=request.user)
                    cart_item = CartItem.objects.filter(
                        cart=user_cart,
                        pet=pet
                    ).first()
                    if cart_item:
                        cart_item.delete()

                # 7. 更新订单总价
                order.total_amount = total_price
                order.save()

                # 8. 返回成功响应，重定向到订单详情页
                return JsonResponse({
                    'success': True,
                    'redirect_url': '/orders/detail/{}/'.format(order.id)
                })

        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'message': '数据格式错误'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'提交订单时发生错误：{str(e)}'
            })

    # 如果不是POST请求，返回错误
    return JsonResponse({
        'success': False,
        'message': '不支持的请求方法'
    })