import time
import uuid
import requests
import hashlib
import base64
import urllib.parse
import json


class SFExpressSDK:
    def __init__(self, partner_id="", checkword="", is_production=False):
        """
        初始化顺丰SDK
        :param partner_id: 丰桥平台顾客编码
        :param checkword: 丰桥平台校验码
        :param is_production: 是否生产环境
        """
        self.partner_id = partner_id
        self.checkword = checkword
        self.is_production = is_production
        self.req_url = "https://sfapi.sf-express.com/std/service" if is_production else "https://sfapi-sbox.sf-express.com/std/service"

    def _generate_signature(self, msg_data, timestamp):
        """生成签名"""
        str_to_sign = urllib.parse.quote_plus(msg_data + timestamp + self.checkword)
        m = hashlib.md5()
        m.update(str_to_sign.encode('utf-8'))
        md5_str = m.digest()
        return base64.b64encode(md5_str).decode('utf-8')

    def _call_api(self, service_code, msg_data):
        """通用API调用方法"""
        request_id = str(uuid.uuid1())
        timestamp = str(int(time.time()))
        msg_digest = self._generate_signature(msg_data, timestamp)

        data = {
            "partnerID": self.partner_id,
            "requestID": request_id,
            "serviceCode": service_code,
            "timestamp": timestamp,
            "msgDigest": msg_digest,
            "msgData": msg_data
        }

        try:
            response = requests.post(self.req_url, data=data)
            return {"success": True, "data": response.text}
        except Exception as e:
            return {"success": False, "error": str(e)}

    # 1. 创建订单 (EXP_RECE_CREATE_ORDER)
    def create_order(self, order_id, cargo_details, contact_info_list,
                     express_type_id=1, pay_method=1, parcel_qty=1,
                     total_weight=0, is_oneself_pickup=0, language="zh-CN",
                     monthly_card="", customs_info=None, extra_info_list=None):
        """
        创建订单
        :param order_id: 订单号
        :param cargo_details: 货物信息列表，格式: [{name, count, weight, ...}]
        :param contact_info_list: 收寄方信息列表，格式: [{contactType, contact, phone, address, ...}]
        :param express_type_id: 快递类型ID
        :param pay_method: 支付方式
        :param parcel_qty: 包裹数量
        :param total_weight: 总重量
        :param is_oneself_pickup: 是否自提
        :param language: 语言
        :param monthly_card: 月结卡号
        :param customs_info: 报关信息
        :param extra_info_list: 额外信息列表
        """
        data = {
            "orderId": order_id,
            "cargoDetails": cargo_details,
            "contactInfoList": contact_info_list,
            "expressTypeId": express_type_id,
            "payMethod": pay_method,
            "parcelQty": parcel_qty,
            "totalWeight": total_weight,
            "isOneselfPickup": is_oneself_pickup,
            "language": language,
            "monthlyCard": monthly_card,
            "customsInfo": customs_info or {},
            "extraInfoList": extra_info_list or []
        }
        return self._call_api("EXP_RECE_CREATE_ORDER", json.dumps(data, ensure_ascii=False))

    # 2. 查询订单 (EXP_RECE_SEARCH_ORDER_RESP)
    def query_order(self, order_id, search_type="1", language="zh-cn"):
        """
        查询订单结果
        :param order_id: 订单号
        :param search_type: 查询类型（1-按订单号）
        :param language: 语言
        """
        data = {
            "searchType": search_type,
            "orderId": order_id,
            "language": language
        }
        return self._call_api("EXP_RECE_SEARCH_ORDER_RESP", json.dumps(data, ensure_ascii=False))

    # 3. 订单确认取消 (EXP_RECE_UPDATE_ORDER)
    def update_order(self, order_id, deal_type):
        """
        订单确认取消
        :param order_id: 订单号
        :param deal_type: 操作类型（2-取消订单）
        """
        data = {
            "dealType": deal_type,
            "orderId": order_id
        }
        return self._call_api("EXP_RECE_UPDATE_ORDER", json.dumps(data, ensure_ascii=False))

    # 4. 订单筛选 (EXP_RECE_FILTER_ORDER_BSP)
    def filter_order(self, filter_type, order_id, contact_infos):
        """
        订单筛选
        :param filter_type: 筛选类型
        :param order_id: 订单号
        :param contact_infos: 收寄方信息列表
        """
        data = [{
            "filterType": filter_type,
            "orderId": order_id,
            "contactInfos": contact_infos
        }]
        return self._call_api("EXP_RECE_FILTER_ORDER_BSP", json.dumps(data, ensure_ascii=False))

    # 5. 路由查询 (EXP_RECE_SEARCH_ROUTES)
    def query_route(self, tracking_number, tracking_type=1, language="0", method_type="1"):
        """
        路由查询
        :param tracking_number: 跟踪号（运单号或订单号）
        :param tracking_type: 1-运单号，2-订单号
        :param language: 语言
        :param method_type: 方法类型
        """
        data = {
            "language": language,
            "trackingType": str(tracking_type),
            "trackingNumber": [tracking_number],
            "methodType": method_type
        }
        return self._call_api("EXP_RECE_SEARCH_ROUTES", json.dumps(data, ensure_ascii=False))

    # 6. 子单号申请 (EXP_RECE_GET_SUB_MAILNO)
    def apply_sub_mailno(self, order_id, parcel_qty):
        """
        子单号申请
        :param order_id: 订单号
        :param parcel_qty: 包裹数量
        """
        data = {
            "orderId": order_id,
            "parcelQty": parcel_qty
        }
        return self._call_api("EXP_RECE_GET_SUB_MAILNO", json.dumps(data, ensure_ascii=False))

    # 7. 清单运费查询 (EXP_RECE_QUERY_SFWAYBILL)
    def query_waybill_fee(self, tracking_num, tracking_type="1"):
        """
        清单运费查询
        :param tracking_num: 跟踪号
        :param tracking_type: 跟踪类型
        """
        data = {
            "trackingNum": tracking_num,
            "trackingType": tracking_type
        }
        return self._call_api("EXP_RECE_QUERY_SFWAYBILL", json.dumps(data, ensure_ascii=False))

    # 8. 退货下单 (EXP_RECE_CREATE_REVERSE_ORDER)
    def create_reverse_order(self, order_id, cargo_details, contact_info_list,
                             language="zh_CN", pay_method=1, express_type_id=1,
                             monthly_card="", send_start_tm=None, refund_amount=0,
                             is_check="1", biz_template_code=""):
        """
        退货下单
        :param order_id: 订单号
        :param cargo_details: 货物信息列表
        :param contact_info_list: 收寄方信息列表
        :param language: 语言
        :param pay_method: 支付方式
        :param express_type_id: 快递类型ID
        :param monthly_card: 月结卡号
        :param send_start_tm: 发送开始时间
        :param refund_amount: 退款金额
        :param is_check: 是否校验
        :param biz_template_code: 业务模板编码
        """
        data = {
            "language": language,
            "orderId": order_id,
            "cargoDetails": cargo_details,
            "contactInfoList": contact_info_list,
            "payMethod": pay_method,
            "expressTypeId": express_type_id,
            "monthlyCard": monthly_card,
            "sendStartTm": send_start_tm or time.strftime("%Y-%m-%d %H:%M:%S"),
            "refundAmount": refund_amount,
            "isCheck": is_check,
            "bizTemplateCode": biz_template_code
        }
        return self._call_api("EXP_RECE_CREATE_REVERSE_ORDER", json.dumps(data, ensure_ascii=False))

    # 9. 退货消单 (EXP_RECE_CANCEL_REVERSE_ORDER)
    def cancel_reverse_order(self, order_id):
        """
        退货消单
        :param order_id: 订单号
        """
        data = {"orderId": order_id}
        return self._call_api("EXP_RECE_CANCEL_REVERSE_ORDER", json.dumps(data, ensure_ascii=False))

    # 10. 派件通知 (EXP_RECE_DELIVERY_NOTICE)
    def delivery_notice(self, waybill_no, data_type="71", language="zh-cn"):
        """
        派件通知
        :param waybill_no: 运单号
        :param data_type: 数据类型
        :param language: 语言
        """
        data = {
            "waybillNo": waybill_no,
            "dataType": data_type,
            "language": language
        }
        return self._call_api("EXP_RECE_DELIVERY_NOTICE", json.dumps(data, ensure_ascii=False))

    # 11. 截单转寄 (EXP_RECE_WANTED_INTERCEPT)
    def wanted_intercept(self, waybill_no, new_dest_address, cancel=False,
                         deliver_date=None, deliver_time_min="09:00",
                         deliver_time_max="12:00", monthly_card_no="",
                         pay_mode="3", role="1", service_code="7"):
        """
        截单转寄
        :param waybill_no: 运单号
        :param new_dest_address: 新地址信息
        :param cancel: 是否取消
        :param deliver_date: 派送日期
        :param deliver_time_min: 最小派送时间
        :param deliver_time_max: 最大派送时间
        :param monthly_card_no: 月结卡号
        :param pay_mode: 支付方式
        :param role: 角色
        :param service_code: 服务代码
        """
        data = {
            "cancel": cancel,
            "waybillNo": waybill_no,
            "newDestAddress": new_dest_address,
            "deliverDate": deliver_date or time.strftime("%Y-%m-%d"),
            "deliverTimeMin": deliver_time_min,
            "deliverTimeMax": deliver_time_max,
            "monthlyCardNo": monthly_card_no,
            "payMode": pay_mode,
            "role": role,
            "serviceCode": service_code
        }
        return self._call_api("EXP_RECE_WANTED_INTERCEPT", json.dumps(data, ensure_ascii=False))

    # 12. 云打印面单 (COM_RECE_CLOUD_PRINT_WAYBILLS)
    def cloud_print_waybills(self, template_code, documents, file_type="pdf"):
        """
        云打印面单打印
        :param template_code: 模板编码
        :param documents: 面单信息列表
        :param file_type: 文件类型
        """
        data = {
            "templateCode": template_code,
            "fileType": file_type,
            "documents": documents
        }
        return self._call_api("COM_RECE_CLOUD_PRINT_WAYBILLS", json.dumps(data, ensure_ascii=False))

    # 13. 揽件服务时间查询 (EXP_EXCE_CHECK_PICKUP_TIME)
    def check_pickup_time(self, address, city_code, address_type=1, send_time=None,
                          sys_code="bsp", version="V1.1"):
        """
        揽件服务时间查询
        :param address: 地址
        :param city_code: 城市代码
        :param address_type: 地址类型
        :param send_time: 发送时间
        :param sys_code: 系统代码
        :param version: 版本号
        """
        data = {
            "address": address,
            "cityCode": city_code,
            "addressType": address_type,
            "sendTime": send_time or time.strftime("%Y-%m-%d %H:%M:%S"),
            "sysCode": sys_code,
            "version": version
        }
        return self._call_api("EXP_EXCE_CHECK_PICKUP_TIME", json.dumps(data, ensure_ascii=False))

    # 14. 运单号合法性校验 (EXP_RECE_VALIDATE_WAYBILLNO)
    def validate_waybillno(self, waybill_no):
        """
        运单号合法性校验
        :param waybill_no: 运单号
        """
        data = {"waybillNo": waybill_no}
        return self._call_api("EXP_RECE_VALIDATE_WAYBILLNO", json.dumps(data, ensure_ascii=False))

    # 15. 路由上传 (EXP_RECE_UPLOAD_ROUTE)
    def upload_route(self, route_list):
        """
        路由上传
        :param route_list: 路由信息列表，格式: [{barScanTm, barOprCode, opCode, waybillNo, ...}]
        """
        return self._call_api("EXP_RECE_UPLOAD_ROUTE", json.dumps(route_list, ensure_ascii=False))

    # 16. 预计派送时间查询 (EXP_RECE_SEARCH_PROMITM)
    def search_promitm(self, search_no, check_type=2, check_nos=None):
        """
        预计派送时间查询
        :param search_no: 查询编号
        :param check_type: 校验类型
        :param check_nos: 校验编号列表
        """
        data = {
            "searchNo": search_no,
            "checkType": check_type,
            "checkNos": check_nos or []
        }
        return self._call_api("EXP_RECE_SEARCH_PROMITM", json.dumps(data, ensure_ascii=False))


# 使用示例
if __name__ == "__main__":
    # 初始化SDK
    sf_sdk = SFExpressSDK(
        partner_id="Y7hHmkqf",
        checkword="ehpA2SxjBT0M0QY74VktZbPSx41xO9gt",
        is_production=False
    )

    # 1. 创建订单示例
    cargo_details = [{
        "amount": 308.0,
        "count": 1.0,
        "name": "君宝牌地毯",
        "unit": "件",
        "weight": 6.6
    }]
    contact_info_list = [{
        "address": "十堰市丹江口市公园路155号",
        "city": "十堰市",
        "company": "清雅轩保健品专营店",
        "contact": "张三丰",
        "contactType": 1,
        "mobile": "17006805888",
        "province": "湖北省"
    }, {
        "address": "湖北省襄阳市襄城区环城东路122号",
        "city": "襄阳市",
        "contact": "郭襄阳",
        "contactType": 2,
        "mobile": "18963828829",
        "province": "湖北省"
    }]
    print("创建订单结果:", sf_sdk.create_order(
        order_id="QIAO-20200728-002",
        cargo_details=cargo_details,
        contact_info_list=contact_info_list,
        total_weight=6
    ))

    # 2. 路由查询示例
    print("路由查询结果:", sf_sdk.query_route(
        tracking_number="SF7444407228423",
        tracking_type=1
    ))

    # 3. 截单转寄示例
    new_address = {
        "address": "粤海街道海阔天空雅居B栋16B",
        "city": "深圳市",
        "contact": "牟星",
        "county": "南山区",
        "phone": "15922226666",
        "province": "广东省"
    }
    print("截单转寄结果:", sf_sdk.wanted_intercept(
        waybill_no="SF444201931741",
        new_dest_address=new_address
    ))