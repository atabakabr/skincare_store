from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from .forms import ProductForm
from products.models import Product,Wishlist
from recommendation.views import recommend_prods_content_based
from accounts.models import CustomUser
from orders.models import order
from django.db.models import Sum
from search.models import browsing_history

#@login_required
def home_page(request):
    if request.user.is_staff:
        return redirect('admin_home')
    prod_ids=recommend_prods_content_based(request)
    products=Product.objects.all()
    recommended_products=Product.objects.filter(id__in=prod_ids) if prod_ids else []
    most_sales=Product.objects.filter(quantity__gt=0).order_by('-sold_quantity')[:8]
    newest=Product.objects.order_by('-created_at')[:8]
    return render(request,'home/home.html',{'products': products,'recommended_products': recommended_products,'newest':newest,'most_sales':most_sales})


@staff_member_required
def admin_home(request):
    products=Product.objects.all()
    if request.method=='POST':
        form=ProductForm(request.POST,request.FILES)
        if form.is_valid():
            form.save()
            return redirect('admin_home')
    else:
        form=ProductForm(request.POST, request.FILES)


    users_count=CustomUser.objects.count()
    total_views=browsing_history.objects.filter(interaction_type='view').count()
    total_sales = browsing_history.objects.filter(interaction_type='cart').aggregate(total=Sum('quantity'))['total'] or 0

    context={
        'form':form,'products':products,"users_count":users_count,"total_views":total_views,"total_sales":total_sales
    }
    return render(request,'home/admin_home.html',context)

@staff_member_required
def edit_product(request,product_id):
    product=get_object_or_404(Product,id=product_id)
    if request.method=="POST":
        form=ProductForm(request.POST,request.FILES,instance=product)
        if form.is_valid():
            form.save()
            return redirect('admin_home')
    else:
        form=ProductForm(instance=product)

    return render(request,"home/edit_product.html",{"form":form,"product":product})


@staff_member_required
def product_delete(request,product_id):
    product=get_object_or_404(Product,id=product_id)
    if request.method=='POST':
        product.delete()
        return redirect('admin_home')
    
    return redirect('admin_home')

@login_required
def wishlist(request):
    if not request.user.is_authenticated:
        return redirect('login')
    

    wishlist_items=Wishlist.objects.filter(user=request.user).select_related('product')

    return render(request, 'wishlist/wishlist.html', {'wishlist_items': wishlist_items})


