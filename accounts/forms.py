from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser
from django.contrib.auth import password_validation
from django.contrib.auth.hashers import check_password

class CustomUserCreationForm(UserCreationForm):
    SKIN_CHOICES=[
        ('dry','خشک'),
        ('oily','چرب'),
        ('combo','ترکیبی'),
        ('sensitive','حساس'),
    ]
    skin_type=forms.ChoiceField(choices=SKIN_CHOICES,required=True,label="نوع پوست")
    concerns=forms.MultipleChoiceField(
        choices=[
            ('acne','جوش'),
            ('redness','قرمزی'),
            ('dark_spots','لک تیره'),
            ('aging','پیری'),
        ],
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="مشکلات پوستی"
    )
    preferences=forms.MultipleChoiceField(
        choices=[
            ('vegan','وگان'),
            ('fragrance_free','بدون عطر'),
            ('spf','دارای SPF'),
        ],
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="ترجیحات محصول"
    )


    class Meta:
        model=CustomUser
        fields=['username','email','password1','password2','skin_type','concerns','preferences']

    def save(self,commit=True):
        user=super().save(commit=False)
        user.skin_type=self.cleaned_data['skin_type']
        user.concerns=self.cleaned_data['concerns']
        user.preferences=self.cleaned_data['preferences']
        if commit:
            user.save()
        return user




class CustomUserEditForm(forms.ModelForm):
    
    SKIN_CHOICES=[
        ('dry','خشک'),
        ('oily','چرب'),
        ('combo','ترکیبی'),
        ('sensitive','حساس'),
    ]

    skin_type=forms.ChoiceField(choices=SKIN_CHOICES, required=True, label="نوع پوست")

    concerns=forms.MultipleChoiceField(
        choices=[
            ('acne','جوش'),
            ('redness','قرمزی'),
            ('dark_spots','لک تیره'),
            ('aging','پیری'),
        ],
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="مشکلات پوستی"
    )

    preferences=forms.MultipleChoiceField(
        choices=[
            ('vegan','وگان'),
            ('fragrance_free','بدون عطر'),
            ('spf','دارای SPF'),
        ],
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="ترجیحات محصول"
    )


    current_password=forms.CharField(
        label="رمز فعلی",
        widget=forms.PasswordInput,
        required=False,
    )

    new_password=forms.CharField(
        label="رمز جدید",
        widget=forms.PasswordInput,
        required=False,
    )

    confirm_password=forms.CharField(
        label="تکرار رمز جدید",
        widget=forms.PasswordInput,
        required=False,
    )

    class Meta:
        model=CustomUser
        fields=['username','email','skin_type','concerns','preferences']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.concerns:
            self.initial['concerns']=self.instance.concerns
        if self.instance.preferences:
            self.initial['preferences']=self.instance.preferences

    def clean(self):
        cleaned_data=super().clean()
        current_password=cleaned_data.get('current_password')
        new_password=cleaned_data.get('new_password')
        confirm_password=cleaned_data.get('confirm_password')

        if current_password or new_password or confirm_password:
            if not current_password or not new_password or not confirm_password:
                raise forms.ValidationError("برای تغییر رمز، همه فیلدهای رمز را پر کن.")
            if not self.instance.check_password(current_password):
                raise forms.ValidationError("رمز فعلی اشتباهه.")
            if new_password!=confirm_password:
                raise forms.ValidationError("رمز جدید و تکرارش یکی نیستن.")
            password_validation.validate_password(new_password, self.instance)

        return cleaned_data

    def save(self,commit=True):
        user=super().save(commit=False)
        user.concerns=self.cleaned_data['concerns']
        user.preferences=self.cleaned_data['preferences']
        new_password=self.cleaned_data.get('new_password')
        if new_password:
            user.set_password(new_password)
        if commit:
            user.save()
        return user
