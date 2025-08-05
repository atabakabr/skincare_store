from django.shortcuts import render
import products.models as pdm

def search(request):
    q=request.GET.get('q')
    skin_type=request.GET.get('skin_type')
    concerns=request.GET.get('concerns')
    ingredients=request.GET.get('ingredients')
    min_price=request.GET.get('min_price')
    max_price=request.GET.get('max_price')
    products=pdm.Product.objects.all()

    if q:
        products=products.filter(name__icontains=q)
    if skin_type:
        products=products.filter(skin_type__name__icontains=skin_type)
    if concerns:
        products=products.filter(concerns_targeted__name__icontains=concerns)
    if ingredients:
        products=products.filter(ingredients__name__icontains=ingredients)

    if min_price:
        products=products.filter(price__gte=min_price)
    if max_price:
        products=products.filter(price__lte=max_price)

    products=products.distinct()

    return render(request, 'search/search.html', {'products': products})
