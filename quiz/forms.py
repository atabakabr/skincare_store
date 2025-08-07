from django import forms
from .models import question

class ScaleQuizForm(forms.Form):
    def __init__(self,*args,**kwargs):
        qstns=kwargs.pop('questions')
        super().__init__(*args, **kwargs)
        for q in qstns:
            self.fields[f"question_{q.id}"]=forms.IntegerField(label=q.text,min_value=1,max_value=10,widget=forms.NumberInput(attrs={'type':'range','step': '1'}))


class PreferencesForm(forms.Form):
    routine_length=forms.ChoiceField(
        label="چند مرحله در روتینت می‌خواهی؟",
        choices=[
            ('short', '2–3 مرحله'),
            ('medium', '4–5 مرحله'),
            ('long', '6+ مرحله'),
        ],
        widget=forms.RadioSelect
    )
    avoid_fragrance=forms.BooleanField(
        label="از محصولات بدون عطر استفاده کنم؟",
        required=False
    )
    use_serum=forms.BooleanField(
        label="دوست داری سرم هم باشه؟",
        required=False
    )
    time_per_day=forms.IntegerField(
        label="حدوداً چقدر وقت برای روتینت در روز داری؟ (دقیقه)",
        min_value=1,
        max_value=60
    )
