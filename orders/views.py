from django.shortcuts import render, redirect, get_object_or_404
from .models import ord_items,order,cart_item
from products.models import Product
from accounts.models import CustomUser
from search.models import browsing_history 

 
def add_to_cart(request, product_id):
    if not request.user.is_authenticated:
        return redirect('login')
    
    
    product=get_object_or_404(Product, id=product_id)
    if product.quantity>0:
        orderer,created=order.objects.get_or_create(user_id=request.user,is_paid=False)
        ord_itms,created=ord_items.objects.get_or_create(product_id=product,ord=orderer,defaults={'price_at_purchase': product.price})

        if not created:
            ord_itms.quantity+=1
            ord_itms.save()

        cart_itm,created=cart_item.objects.get_or_create(ord=orderer,defaults={'quantity': 1})
        if not created:
            cart_itm.quantity+=1
            cart_itm.save()
    return redirect(request.META.get('HTTP_REFERER', '/'))


def delete_from_cart(request, product_id):
    if not request.user.is_authenticated:
        return redirect('login')

    product=get_object_or_404(Product, id=product_id)
    orderer=order.objects.get(user_id=request.user,is_paid=False)
    crt_itm=cart_item.objects.get(ord=orderer)
    ord_itm=ord_items.objects.filter(ord=orderer,product_id=product).first()
    if ord_itm and crt_itm:
        if ord_itm.quantity<=1:
            ord_itm.delete()
        else:
            #print('yes')
            crt_itm.quantity-=1
            ord_itm.quantity-=1
            ord_itm.save()
            crt_itm.save()


    return redirect(request.META.get('HTTP_REFERER', '/'))

def cart(request):
    if not request.user.is_authenticated:
        return redirect('login')

    try:
        orderer=order.objects.get(user_id=request.user,is_paid=False)
    except order.DoesNotExist:
        return render(request, 'orders/cart.html', {'items': [], 'total': 0})
    if not orderer.is_paid:
        items=ord_items.objects.filter(ord=orderer)
        products=[]
        total_price=0

        for item in items:
            product=item.product_id
            product.quantity=item.quantity
            product.price=item.price_at_purchase
            total_price+=item.price_at_purchase*item.quantity
            products.append({
                'id': item.product_id.id,
                'name': item.product_id.name,
                'image': item.product_id.image_url,
                'quantity': item.quantity,
                'price': item.price_at_purchase,
                'total': item.price_at_purchase * item.quantity,})

        return render(request,'orders/cart.html',{'items': products,'total': total_price})


def finalize_order(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    try:
        orderer=order.objects.get(user_id=request.user,is_paid=False)
    except order.DoesNotExist:
        return redirect('cart')

    orderer.is_paid=True
    orderer.save()
    
    for items in ord_items.objects.filter(ord=orderer):
        #print(items.product_id)
        obj,created = browsing_history.objects.update_or_create(
                user_id=orderer.user_id,
                product_id=items.product_id,
                interaction_type='cart',
            )
        if not created:
            obj.quantity+=(1*items.quantity)
            obj.save()
        prod=Product.objects.get(id=items.product_id.id)
        prod.sold_quantity+=(1*items.quantity)
        prod.quantity-=(1*items.quantity)
        prod.save()
 


    cart_item.objects.filter(ord=orderer).delete()

    return redirect('success_page')

    
def success_page(request):
    return render(request,'orders/success.html')
    
