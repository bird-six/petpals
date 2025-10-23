import json
import logging
from alipay.aop.api.AlipayClientConfig import AlipayClientConfig
from alipay.aop.api.DefaultAlipayClient import DefaultAlipayClient
from alipay.aop.api.domain.AlipayTradePagePayModel import AlipayTradePagePayModel
from alipay.aop.api.domain.AlipayTradeRefundModel import AlipayTradeRefundModel
from alipay.aop.api.request.AlipayTradePagePayRequest import AlipayTradePagePayRequest
from alipay.aop.api.request.AlipayTradeRefundRequest import AlipayTradeRefundRequest
from alipay.aop.api.util.SignatureUtils import verify_with_rsa
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from apps.cart.models import Cart, CartItem
from apps.orders.models import Order, OrderItem
from apps.pets.models import Pet
from apps.users.models import Address
from petpals import settings


@login_required
def checkout(request, pet_id=None):
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
    else:
        if pet_id:
            pet = get_object_or_404(Pet, id=pet_id)
            user_addresses = Address.objects.filter(user=request.user)
            # 创建一个简单的类来模拟 CartItem 的结构
            class PetItem:
                def __init__(self, pet):
                    self.pet = pet
                    self.quantity = 1
            # 将单个宠物对象包装成列表
            selected_items = [PetItem(pet)]
            total_price = pet.price
        return render(request, 'orders/orders.html', {
            'selected_items': selected_items,
            'total_price': total_price,
            'user_addresses': user_addresses
        })


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
        # 检查是否包邮
        if total_amount < 199:
            total_amount += 15
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






# 通知参数处理的工具函数
def get_dic_sorted_params(org_dic_params):
    content = ''
    org_dic_params.pop('sign')
    org_dic_params.pop('sign_type')  # 去除sign、sigh_type
    new_list = sorted(org_dic_params, reverse=False)  # 待验签参数进行排序
    for i in new_list:
        p = i + '=' + org_dic_params.get(i) + '&'
        content += p
    sorted_params = content.strip('&')  # 重组字符串，将{k:v}形式的字典类型原始响应值--》转换成'k1=v1&k2=v2'形式的字符串格式
    return sorted_params


# 支付宝同步通知回调视图函数
def alipay_return(request):
    # 获取支付宝返回的所有参数
    params = request.GET.dict()
    # 提取签名
    sign = params.get('sign')
    # 对通知参数进行处理
    org_message = get_dic_sorted_params(params)
    # 转换成字节串
    message = bytes(org_message, encoding='utf-8')

    # 验证签名
    verified = verify_with_rsa(
        public_key=settings.ALIPAY_SETTINGS['alipay_public_key'],
        message=message,
        sign=sign,
    )
    if verified:
        # 验签成功且交易状态有效（仅用于前端展示）
        order_number = params.get("out_trade_no")  # 商户订单号
        order = get_object_or_404(Order, order_number=order_number)
        return render(request, "orders/success.html", {"order": order})
    else:
        # 验签失败或交易状态异常
        order_number = params.get("out_trade_no")  # 商户订单号
        order = get_object_or_404(Order, order_number=order_number)
        return render(request, "orders/fail.html", {"order": order})

# 支付宝异步通知回调视图函数
@csrf_exempt    # 禁用CSRF防护，确保支付宝异步通知可以正常接收
def alipay_notify(request):
    if request.method == 'POST':
        # 1. 获取支付宝发送的通知参数（POST形式）
        params = request.POST.dict()
        # 2. 提取签名（用于验证）
        sign = params.get('sign')
        # 3. 对通知参数进行处理
        org_message = get_dic_sorted_params(params)
        # 4. 转换成字节串
        message = bytes(org_message, encoding='utf-8')

        # 5. verify_with_rsa方法验证签名
        verified = verify_with_rsa(
            public_key=settings.ALIPAY_SETTINGS['alipay_public_key'],
            message=message,
            sign=sign,
        )

        # 6. 检查验证状态
        if not verified:
            print("支付宝异步通知：签名验证失败")
            return HttpResponse("fail")  # 签名验证失败返回fail，这是支付宝接口的硬性要求

        trade_status = params.get('trade_status')
        if trade_status not in ['TRADE_SUCCESS', 'TRADE_FINISHED']:
            logging.info(f"支付未成功，状态：{trade_status}")
            return HttpResponse("success")  # 支付宝要求非成功状态也返回success
        # 7. 数据更新逻辑
        try:
            # 获取支付数据
            out_trade_no = params.get('out_trade_no')  # 订单号
            gmt_create = params.get('gmt_create')  # 订单创建时间
            gmt_payment = params.get('gmt_payment')  # 支付时间
            trade_no = params.get('trade_no')  # 支付宝交易流水号
            order = Order.objects.get(order_number=out_trade_no)

            # 幂等性处理：如果已经支付成功，直接返回
            if order.status == "已支付":
                return HttpResponse("success")

            order.pay_time = gmt_payment  # 写入支付时间
            order.create_time = gmt_create  # 写入订单创建时间
            order.status = "已支付"  # 更新订单状态
            order.trade_no = trade_no  # 写入支付宝交易流水号
            order.save()
            logging.info(f"订单{out_trade_no}支付成功，状态已更新")
        except Exception as e:
            logging.error(f"处理订单失败：{str(e)}")
            return HttpResponse("fail")
        return HttpResponse("success")
    return HttpResponse("fail")  # 非POST请求返回fail

def refund(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    # 初始化客户端配置对象AlipayClientConfig
    alipay_client_config = AlipayClientConfig()  # 初始化支付宝客户端配置对象
    alipay_client_config.server_url = 'https://openapi-sandbox.dl.alipaydev.com/gateway.do'  # 沙箱环境
    alipay_client_config.app_id = settings.ALIPAY_SETTINGS['appid']  # 应用ID
    alipay_client_config.app_private_key = settings.ALIPAY_SETTINGS['app_private_key']  # 应用私钥
    alipay_client_config.alipay_public_key = settings.ALIPAY_SETTINGS['alipay_public_key']  # 支付宝公钥
    alipay_client_config.sign_type = settings.ALIPAY_SETTINGS['sign_type']  # 签名类型（默认RSA2）

    # 创建客户端DefaultAlipayClient实例
    alipay_client = DefaultAlipayClient(alipay_client_config)

    # 实例化退款参数模型AlipayTradeRefundModel
    refund_model = AlipayTradeRefundModel()
    refund_model.out_trade_no = order.order_number  # 商户订单号
    refund_model.refund_amount = str(order.total_amount)  # 退款金额（与订单金额一致）
    refund_model.refund_reason = "用户申请退款"  # 退款原因

    # 实例化退款请求类AlipayTradeRefundRequest
    refund_request = AlipayTradeRefundRequest(biz_model=refund_model)
    refund_result = alipay_client.execute(refund_request)

    return HttpResponse(refund_result)


def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    from libs.sf_sdk import SFExpressSDK
    sf_sdk = SFExpressSDK(
        partner_id="YDO0OKA0",
        checkword="cEF48gJFooF4wd8R7hesJEIV6aJgzRdq",
        is_production=False
    )
    message = {
      "success": True,
      "data": {
        "apiErrorMsg": "",
        "apiResponseID": "00019A0B6061D04FDEC1EBBDFB37D94E",
        "apiResultCode": "A1000",
        "apiResultData": {
          "success": True,
          "errorCode": "S0000",
          "errorMsg": None,
          "msgData": {
            "routeResps": [
              {
                "mailNo": "SF1234567890123",
                "routes": [
                  {
                    "acceptAddress": "深圳市南山区科技园",
                    "acceptTime": "2025-10-22 18:04:17",
                    "remark": "顺丰速运 已收取快件（快递员：张明，电话：13800138000）",
                    "opCode": "50"
                  },
                  {
                    "acceptAddress": "深圳市转运中心",
                    "acceptTime": "2025-10-22 20:30:52",
                    "remark": "快件已到达 深圳市转运中心",
                    "opCode": "30"
                  },
                  {
                    "acceptAddress": "深圳市转运中心",
                    "acceptTime": "2025-10-22 22:15:36",
                    "remark": "快件正发往 广州市转运中心",
                    "opCode": "40"
                  },
                  {
                    "acceptAddress": "广州市转运中心",
                    "acceptTime": "2025-10-23 06:48:21",
                    "remark": "快件已到达 广州市转运中心",
                    "opCode": "30"
                  },
                  {
                    "acceptAddress": "广州市天河区网点",
                    "acceptTime": "2025-10-23 09:20:10",
                    "remark": "快件已到达 广州市天河区网点",
                    "opCode": "30"
                  },
                  {
                    "acceptAddress": "广州市天河区网点",
                    "acceptTime": "2025-10-23 10:05:47",
                    "remark": "快件正在派送中（派送员：李华，电话：13900139000）",
                    "opCode": "80"
                  },
                  {
                    "acceptAddress": "广州市天河区天河路XX号",
                    "acceptTime": "2025-10-23 11:32:08",
                    "remark": "快件已签收（签收人：王**，签收方式：本人签收）",
                    "opCode": "90"
                  }
                ],
                "orderId": "SF7444407228423",
                "senderName": "陈先生",
                "receiverName": "王先生",
                "productType": "普通货物"
              }
            ]
          }
        }
      }
    }

    routes = message["data"]["apiResultData"]["msgData"]["routeResps"][0]["routes"]
    print(routes)
    return render(request, "orders/order_detail.html", {"order": order, "routes": routes})
