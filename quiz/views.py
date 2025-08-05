from django.shortcuts import render, redirect
from django.contrib import messages
import requests
import json
import uuid
from .models import question, quiz_results
from .forms import ScaleQuizForm
from products.models import Product

API_KEY = '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'
HF_CHAT_URL = "https://router.huggingface.co/v1/chat/completions"

from django.shortcuts import render, redirect
from django.contrib import messages
import requests
from .models import question, quiz_results
from .forms import ScaleQuizForm
from products.models import Product

API_KEY    = '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'
HF_CHAT_URL = "https://router.huggingface.co/v1/chat/completions"

def ask_mistral(prompt: str) -> str:
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type":  "application/json",
    }
    payload = {
        "model":       "deepseek-ai/DeepSeek-R1-0528:novita",
        "messages":    [{"role": "user", "content": prompt}],
        "temperature": 0.7,
        "max_tokens":  512,
    }
    try:
        resp = requests.post(HF_CHAT_URL, headers=headers, json=payload, timeout=30)
        resp.raise_for_status()
    except requests.RequestException as e:
        return f"خطا در تماس با API: {e}"
    data = resp.json()
    return data['choices'][0]['message']['content']

def get_quiz(request):
    qstns = question.objects.all()

    if request.method == 'POST':
        form = ScaleQuizForm(request.POST, questions=qstns)
        if not form.is_valid():
            return render(request, 'quiz/quiz.html', {'form': form})

        # 1) جمع‌آوری پاسخ‌ها
        user_answers = {
            q.text: form.cleaned_data[f"question_{q.id}"]
            for q in qstns
        }

        # 2) ساخت بخش اول پرامپت (سوال‌ها)
        prompt = (
            "You are a skincare expert assistant. "
            "Based on the user's responses to a skin quiz in Persian (each scored 0 to 10), "
            "determine their skin type and concerns, and recommend a morning and night skincare routine "
            "using **only** the provided list of products.\n\n"
            "Each routine should include up to 4-5 steps (cleanser, treatment/serum, moisturizer, sunscreen (for AM), etc.). "
            "Pick the most suitable products from the list for the user's skin type and concerns.\n\n"
            "User responses:\n"
        )
        for text, score in user_answers.items():
            prompt += f"Question: {text} → Score: {score}/10\n"

        # 3) الحاق لیست محصولات داینامیک
        prompt += "\nAvailable products (with tags): [\n"
        for p in Product.objects.all():
            # اگر M2M داری:
            if hasattr(p, 'tags'):
                tag_list = list(p.tags.values_list('name', flat=True))
            else:
                tag_list = p.tags.split(';') if p.tags else []
            prompt += f'  {{"name": "{p.name}", "tags": {tag_list}}},\n'
        prompt += "]\n\n"

        # 4) دستور نهایی برای خروجی JSON
        prompt += (
            "Output **ONLY** a valid JSON object with the following structure:\n"
            "{\n"
            '  "skin_type": "dry|oily|combination|normal|sensitive",\n'
            '  "concerns": ["acne","dryness","dark_spots","redness","wrinkles","oiliness"],\n'
            '  "routine": {\n'
            '    "AM": [\n'
            '      {"step": "Cleanser",    "product": ""},\n'
            '      {"step": "Serum",        "product": ""},\n'
            '      {"step": "Moisturizer",  "product": ""},\n'
            '      {"step": "Sunscreen",    "product": ""}\n'
            '    ],\n'
            '    "PM": [\n'
            '      {"step": "Cleanser",    "product": ""},\n'
            '      {"step": "Treatment",   "product": ""},\n'
            '      {"step": "Moisturizer", "product": ""}\n'
            '    ]\n'
            "  }\n"
            "}\n"
            "**CRITICAL**: Return **ONLY** the JSON. Do NOT include any explanations or comments."
        )

        # 5) ارسال به API و دریافت پاسخ
        ai_response = ask_mistral(prompt)
        print(ai_response)
        try:
            result = json.loads(ai_response)
        except json.JSONDecodeError:
            messages.error(request, "خطا در دریافت پاسخ معتبر از مدل.")
            return redirect('get_quiz')


        return render(request, 'quiz/result.html', {'ai_response': result})

    else:
        form = ScaleQuizForm(questions=qstns)
        return render(request, 'quiz/quiz.html', {'form': form})

