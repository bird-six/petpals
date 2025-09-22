from apps.cart.models import Cart


def cart_item_count(request):
    count = 0
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()
        if cart:
            count = cart.get_item_count()
    return {'cart_item_count': count}


def cart_item_kind(request):
    kind = 0
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()
        if cart:
            kind = cart.items.values('pet').distinct().count()
    return {'cart_item_kind': kind}