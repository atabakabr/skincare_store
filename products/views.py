from django.shortcuts import render, get_object_or_404, redirect
from products.models import UserRating
from products.models import Product
from search.models import browsing_history 
from products.models import Wishlist
from orders.models import ord_items,order

def view_product(request,product_id):
    product=Product.objects.get(id=product_id)
    user_rating=None
    if request.user.is_authenticated:
        user_rating_obj=UserRating.objects.filter(user=request.user,product=product).first()
        if user_rating_obj:
            user_rating=user_rating_obj.rating

        obj,created = browsing_history.objects.update_or_create(
            user_id=request.user,
            product_id=product,
            interaction_type='view',
        )
        if not created:
            obj.quantity+=1
            obj.save()
        try:
            ordrr=order.objects.get(user_id=request.user,is_paid=False)
            if ordrr:
                ord_itm=ord_items.objects.filter(ord=ordrr,product_id=product).first()
        except:
            ord_itm=None

    

    return render(request, 'products/details.html', {'product':product , 'user_rating':user_rating , 'ord_itm':ord_itm})

def rate_product(request,product_id):
    if request.method=='POST' and request.user.is_authenticated:
        product=get_object_or_404(Product, id=product_id)


        user_rating_val=int(request.POST.get('rating'))
        user_rating,created=UserRating.objects.get_or_create(user=request.user,product=product,defaults={'rating': user_rating_val})
        if not created:
                    user_rating.rating = user_rating_val
                    user_rating.save()

        tscore=(product.rating*product.rate_quantity)+user_rating_val
        product.rate_quantity+=1
        product.rating=tscore/product.rate_quantity

        product.save()




    return redirect('view_product', product_id=product.id)


def add_wishlist(request,product_id):
    if request.user.is_authenticated:
        product = get_object_or_404(Product, id=product_id)
        Wishlist.objects.get_or_create(user=request.user, product=product)
        obj,created = browsing_history.objects.update_or_create(
            user_id=request.user,
            product_id=product,
            interaction_type='wishlist',
        )


    return redirect(request.META.get('HTTP_REFERER', '/'))


def delete_from_wishlist(request,product_id):
    if request.user.is_authenticated:
        prod=Product.objects.get(id=product_id)
        itm=Wishlist.objects.get(user=request.user,product=prod)
        itm.delete()

        obj,created = browsing_history.objects.update_or_create(
            user_id=request.user,
            product_id=prod,
            interaction_type='wishlist',
        )
        obj.delete()
    
    return redirect(request.META.get('HTTP_REFERER', '/'))
    