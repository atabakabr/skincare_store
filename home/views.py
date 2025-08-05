from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from .forms import ProductForm
from products.models import Product,Wishlist

#@login_required
def home_page(request):
    if request.user.is_staff:
        return redirect('admin_home')
    products=Product.objects.all()
    return render(request,'home/home.html',{'products': products})


@staff_member_required
def admin_home(request):
    products=Product.objects.all()
    if request.method=='POST':
        form=ProductForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('admin_home')
    else:
        form=ProductForm()

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


