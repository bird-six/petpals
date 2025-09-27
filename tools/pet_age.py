from datetime import date

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