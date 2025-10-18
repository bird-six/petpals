import json

from alipay.aop.api.AlipayClientConfig import AlipayClientConfig
from alipay.aop.api.DefaultAlipayClient import DefaultAlipayClient
from alipay.aop.api.domain.AlipayTradePagePayModel import AlipayTradePagePayModel
from alipay.aop.api.request.AlipayTradePagePayRequest import AlipayTradePagePayRequest
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from apps.cart.models import Cart, CartItem
from apps.orders.models import Order, OrderItem
from apps.pets.models import Pet
from apps.users.models import Address
from petpals import settings


@login_required
def order(request):
    if request.method == 'POST':
        # 获取选中的宠物商品ID
        pet_ids = request.POST.getlist('pet_ids')
        if not pet_ids:
            return redirect('cart:cart')  # 无商品ID则返回购物车

        # 获取用户购物车
        user_cart = Cart.objects.get(user=request.user)
        selected_items = CartItem.objects.filter(
            cart=user_cart,
            pet_id__in=pet_ids  # 只保留用户购物车中存在的商品
        )
        total_price = sum(item.get_total_price() for item in selected_items)
        # 获取用户地址
        user_addresses = Address.objects.filter(user=request.user)

        return render(request, 'orders/orders.html', {
            'selected_items': selected_items,
            'total_price': total_price,
            'user_addresses': user_addresses
        })

    return render(request, 'orders/orders.html')


@login_required  # 确保用户已登录
def order_create(request):
    if request.method == 'POST':
        # 解析请求体中的JSON数据
        data = json.loads(request.body.decode('utf-8'))
        # 获取收货地址
        address = get_object_or_404(Address, id=data['address_id'], user=request.user)
        # 计算订单总金额
        total_amount = 0
        for item in data['items']:
            total_amount += float(item['price']) * int(item['quantity'])

        # 创建订单
        order = Order.objects.create(
            user=request.user,
            address=address,
            total_amount=total_amount,
            payment_method=data['payment_method'],
            remark=data.get('remarks', '')
        )
        # 为每个商品创建订单项
        for item_data in data['items']:
            pet = get_object_or_404(Pet, id=item_data['pet_id'])
            quantity = int(item_data['quantity'])
            price = float(item_data['price'])

            OrderItem.objects.create(
                order=order,
                pet=pet,
                price=price,
                count=quantity,
                total_price=price * quantity
            )
        return redirect('orders:pay', order_id=order.id)
    # 非POST请求返回错误
    return JsonResponse({'success': False, 'message': '无效的请求方法'})

@login_required
def pay(request, order_id):
    # 获取订单信息
    order = get_object_or_404(Order, id=order_id, user=request.user)

    # 如果订单不存在，返回错误
    if not order:
        return JsonResponse({'success': False, 'message': '订单不存在'})

    # 如果订单不是待支付状态，不进行支付
    if order.status != '待支付':
        return JsonResponse({'success': False, 'message': '订单状态不正确'})


    # 初始化客户端配置对象AlipayClientConfig
    alipay_client_config = AlipayClientConfig()  # 初始化支付宝客户端配置对象
    alipay_client_config.server_url = 'https://openapi-sandbox.dl.alipaydev.com/gateway.do'  # 沙箱环境
    alipay_client_config.app_id = settings.ALIPAY_SETTINGS['appid']  # 应用ID
    alipay_client_config.app_private_key = settings.ALIPAY_SETTINGS['app_private_key']  # 应用私钥
    alipay_client_config.alipay_public_key = settings.ALIPAY_SETTINGS['alipay_public_key']  # 支付宝公钥
    alipay_client_config.sign_type = settings.ALIPAY_SETTINGS['sign_type']  # 签名类型（默认RSA2）

    # 创建客户端DefaultAlipayClient实例
    alipay_client = DefaultAlipayClient(alipay_client_config)

    # 创建订单参数模型
    page_pay_model = AlipayTradePagePayModel()
    page_pay_model.out_trade_no = order.order_number  # 商户订单号（唯一）
    page_pay_model.total_amount = "{0:.2f}".format(order.total_amount)  # 订单金额
    page_pay_model.subject = f"PetPals订单-{order.order_number}"  # 订单标题
    page_pay_model.product_code = "FAST_INSTANT_TRADE_PAY"  # 销售产品码

    # 创建支付请求对象
    page_pay_request = AlipayTradePagePayRequest(biz_model=page_pay_model)  # 关联订单参数模型
    page_pay_request.return_url = settings.ALIPAY_SETTINGS["app_return_url"]  # 同步回调地址（用户支付后跳转）
    page_pay_request.notify_url = settings.ALIPAY_SETTINGS["app_notify_url"]  # 异步通知地址（核心状态通知）

    # 生成支付链接，前端跳转支付页面
    pay_url = alipay_client.page_execute(page_pay_request,
                                         http_method='GET')  # 调用page_execute方法生成支付链接（http_method可选"GET"或"POST"）
    return HttpResponse(f'<script>window.location.href="{pay_url}";</script>')  # 返回支付URL，前端跳转至支付宝支付页面
