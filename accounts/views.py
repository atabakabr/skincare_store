from django.shortcuts import render, redirect
from .forms import CustomUserCreationForm, CustomUserEditForm
from .models import CustomUser
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from orders.models import order, ord_items


def signup_view(request):
    if request.method=='POST':
        form=CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form=CustomUserCreationForm()
    return render(request,'accounts/signup.html',{'form': form})

@login_required
def show_profile(request):
    
    return render(request,'accounts/profile.html',{'user':request.user})

    
@login_required
def edit_profile(request):
    user=request.user

    if request.method=='POST':
        form=CustomUserEditForm(request.POST, instance=user)
        if form.is_valid():
            user=form.save()
            update_session_auth_hash(request, user)
            
            return redirect('show_profile')
    else:
        form=CustomUserEditForm(instance=user)

    return render(request,'accounts/edit_profile.html', {'form':form})

def faq(request):
    return render(request,'accounts/faq.html')

def show_purchase_items(request):
    user=request.user
    ordr=order.objects.filter(user_id=user.id,is_paid=True)
    orders=[]
    for o in ordr:
        items=ord_items.objects.filter(ord=o)
        orders.append({
            'order':o,
            'items':items
        })
    
    return render(request, 'accounts/show_purchase_items.html', {'orders': orders})
