from django import forms
from .models import question

class ScaleQuizForm(forms.Form):
    def __init__(self,*args,**kwargs):
        qstns=kwargs.pop('questions')
        super().__init__(*args, **kwargs)
        for q in qstns:
            self.fields[f"question_{q.id}"]=forms.IntegerField(label=q.text,min_value=1,max_value=10,widget=forms.NumberInput(attrs={'type':'range','step': '1'}))