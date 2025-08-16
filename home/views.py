from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from .forms import ProductForm
from products.models import Product,Wishlist
from recommendation.views import recommend_prods_content_based
#@login_required
def home_page(request):
    if request.user.is_staff:
        return redirect('admin_home')
    prod_ids=recommend_prods_content_based(request)
    products=Product.objects.all()
    recommended_products=Product.objects.filter(id__in=prod_ids) if prod_ids else []
    return render(request,'home/home.html',{'products': products,'recommended_products': recommended_products})


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

    context={
        'form':form,
        'products':products,
    }
    return render(request,'home/admin_home.html',context)

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


