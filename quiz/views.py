from django.shortcuts import render, redirect
from django.contrib import messages
from .models import question, quiz_results
from .forms import ScaleQuizForm
from products.models import Product,SkinType,Concern
from .forms import PreferencesForm

weights = {
    1: {'dry': 0.7, 'sensitive': 0.3},
    2: {'oily': 0.8, 'acne': 0.2},
    3: {'oily': 0.5, 'sensitive': 0.5},
    4: {'sensitive': 1.0},
    5: {'oily': 0.6, 'combination': 0.4},
    6: {'dry': 0.8},
    7: {'sensitive': 0.9},
    8: {'acne': 0.9},
    9: {'oily': 0.7, 'sensitive': 0.3},
    10: {'combination': 1.0},
    11: {'eyebag': 1.0},
    12: {'acne': 0.7, 'sensitive': 0.3},
    13: {'sensitive': 1.0},
    14: {'dry': 0.8},
    15: {'oily': 0.6, 'acne': 0.4},
    16: {'acne': 0.8, 'pigmentation': 0.2},
    17: {'oily': 1.0},
    18: {'oily': 0.7},
    19: {'sensitive': 1.0},
    20: {'sensitive': 1.0},
    21: {'wrinkles': 1.0},
    22: {'wrinkles': 0.7, 'dullness': 0.3},
    23: {'acne': 0.7, 'oily': 0.3},
    24: {'acne': 0.8, 'hormonal': 0.2},
    25: {'dullness': 1.0},
    26: {'oiliness': 0.6, 'texture': 0.4},
    27: {'sensitive': 0.9},
    28: {'sensitive': 1.0},
    29: {'redness': 0.8, 'sensitive': 0.2},
    30: {'combination': 1.0},
    31: {'combination': 0.6, 'oily': 0.4},
    32: {'texture': 1.0},
    33: {'sensitive': 0.5, 'hormonal': 0.5},
    34: {'dry': 0.7, 'flaky': 0.3},
    35: {'all': 1.0},
    36: {'acne': 0.8, 'sensitive': 0.2},
    37: {'dry': 0.5, 'oily': 0.5},
    38: {'sensitive': 0.9},
    39: {'dry': 0.6, 'urban_damage': 0.4},
    40: {'dry': 0.5, 'oily': 0.5},
}



skin_types=SkinType.objects.all()
concerns=Concern.objects.all()


def get_quiz(request):
    score={}
    top_concerns=[]
    sk_tp_sc=0
    sk_tp=None
    qstn=question.objects.all()
    if request.method=='POST':
        form=ScaleQuizForm(request.POST, questions=qstn)
        if form.is_valid():
            for q in qstn:
                v=form.cleaned_data.get(f'question_{q.id}', 0)
                for e in weights[q.id]:
                    if e in score:
                        score[e]+=v*weights[q.id][e]
                    else:
                        score[e]=v*weights[q.id][e]

            for c in concerns:
                if (f'{c.name.lower()}' in score) and score[f'{c.name.lower()}']>6:
                    top_concerns.append(c)

            for s in skin_types:
                if (f'{s.name.lower()}' in score) and score[f'{s.name.lower()}']>sk_tp_sc:
                    sk_tp_sc=score[f'{s}']
                    sk_tp=s
            quiz=quiz_results.objects.create(
                user=request.user,
                skin_type=sk_tp
            )
            quiz.concerns.add(*top_concerns)
            quiz.save()
            request.session['quiz_id']=str(quiz.quiz_id)
            
            return render(request,'quiz/result.html', {
                'result':{
                    'skin_type':sk_tp,
                    'concerns':top_concerns,
                    'routine':{}
                }
            })

            

    else:
        form=ScaleQuizForm(questions=qstn)

    return render(request,'quiz/quiz.html',{'form':form})

#________________________________________________________

def second_quiz(request):
    quiz_id=request.session.get('quiz_id')
    quiz=quiz_results.objects.get(quiz_id=quiz_id)

    if request.method=='POST':
        form=PreferencesForm(request.POST)
        if form.is_valid():
            quiz.preferences=form.cleaned_data
            quiz.save()
            return redirect('show_routine')
    else:
        form=PreferencesForm()

    return render(request,'quiz/second_quiz.html',{
        'form':form,
        'skin_type':quiz.skin_type.name,
        'concerns':[c.name for c in quiz.concerns.all()],
    })

def show_routine(request):
	quiz_id=request.session.get('quiz_id')
	quiz=quiz_results.objects.get(quiz_id=quiz_id)

	skin=quiz.skin_type.name.lower()
	concerns=[c.name.lower() for c in quiz.concerns.all()]
	prefs=quiz.preferences or {}
	routine={'AM':[],'PM':[]}

	if Product.objects.filter(category='cleaner',skin_type__name__iexact=skin).exists():
		cleaner=Product.objects.filter(category='cleaner',skin_type__name__iexact=skin).first()
		routine['AM'].append(cleaner)
		routine['PM'].append(cleaner)

	if Product.objects.filter(category='moisturizer',skin_type__name__iexact=skin).exists():
		moisturizer=Product.objects.filter(category='moisturizer',skin_type__name__iexact=skin).first()
		routine['AM'].append(moisturizer)
		routine['PM'].append(moisturizer)

	if Product.objects.filter(tags__name__icontains='spf',skin_type__name__iexact=skin).exists():
		sunscreen=Product.objects.filter(tags__name__icontains='spf',skin_type__name__iexact=skin).first()
		routine['AM'].append(sunscreen)

	if prefs.get('use_serum'):
		if 'acne' in concerns:
			if Product.objects.filter(category='serum',concerns_targeted__name__iexact='acne').exists():
				serum_bha=Product.objects.filter(category='serum',concerns_targeted__name__iexact='acne').first()
				routine['PM'].append(serum_bha)

		if 'wrinkles' in concerns or prefs.get('routine_length')!='short':
			if Product.objects.filter(category='serum',concerns_targeted__name__icontains='wrinkle').exists():
				serum_retinol=Product.objects.filter(category='serum',concerns_targeted__name__icontains='wrinkle').first()
				routine['PM'].append(serum_retinol)

		if 'dryness' in concerns:
			if Product.objects.filter(category='serum',concerns_targeted__name__icontains='dry').exists():
				serum_hyaluronic=Product.objects.filter(category='serum',concerns_targeted__name__icontains='dry').first()
				routine['AM'].append(serum_hyaluronic)

		if 'redness' in concerns or skin=='sensitive':
			if Product.objects.filter(category='serum',concerns_targeted__name__icontains='red').exists():
				anti_redness=Product.objects.filter(category='serum',concerns_targeted__name__icontains='red').first()
				routine['AM'].append(anti_redness)



	length=prefs.get('routine_length')

	if length=='medium':
		if 'eyebag' in concerns:
			if Product.objects.filter(category='moisturizer',concerns_targeted__name__icontains='eyebag').exists():
				eye_cream=Product.objects.filter(category='moisturizer',concerns_targeted__name__icontains='eyebag').first()
				routine['PM'].append(eye_cream)

	elif length=='long':
		if Product.objects.filter(tags__name__icontains='sleeping').exists():
			sleeping_mask=Product.objects.filter(tags__name__icontains='sleeping').first()
			routine['PM'].append(sleeping_mask)

	return render(request,'quiz/routine.html',{
		'routine':routine,
		'skin_type':quiz.skin_type.name,
		'concerns':quiz.concerns.all(),
		'preferences':prefs,
	})
