from django import forms
from products.models import Product, SkinType, Concern, Ingredient, Tag

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'name', 'brand', 'category',
            'skin_type', 'concerns_targeted',
            'ingredients', 'price',
            'image_url', 'tags','quantity','image',
        ]
        widgets = {
            'skin_type': forms.CheckboxSelectMultiple(),
            'concerns_targeted': forms.CheckboxSelectMultiple(),
            'ingredients': forms.CheckboxSelectMultiple(),
            'tags': forms.CheckboxSelectMultiple(),
            'quantity':forms.NumberInput(),
        }
