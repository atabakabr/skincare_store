#!/usr/bin/env python
import os
import sys
import csv
import django

# 1. مسیر پروژه (جایی که manage.py هست) را اضافه می‌کنیم
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)

# 2. ست کردن DJANGO_SETTINGS_MODULE
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'skincare_store.settings')

# 3. راه‌اندازی Django
django.setup()

from products.models import Product, SkinType, Concern, Tag, Ingredient

CSV_PATH = os.path.join(PROJECT_ROOT, 'products_1000.csv')

def seed_m2m_values(csv_path):
    """ابتدا همهٔ مقادیر یونیک مانی تو مانی را از CSV بخوان و داخل جداول مربوطه بساز."""
    skin_types = set()
    concerns = set()
    tags = set()
    ingredients = set()

    with open(csv_path, encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            skin_types.update([s.strip() for s in row.get('skin_types', '').split(';') if s.strip()])
            concerns.update([c.strip() for c in row.get('concerns_targeted', '').split(';') if c.strip()])
            tags.update([t.strip() for t in row.get('tags', '').split(';') if t.strip()])
            ingredients.update([i.strip() for i in row.get('ingredients', '').split(';') if i.strip()])

    # bulk get_or_create برای هر مجموعه
    for name in skin_types:
        SkinType.objects.get_or_create(name=name)
    for name in concerns:
        Concern.objects.get_or_create(name=name)
    for name in tags:
        Tag.objects.get_or_create(name=name)
    for name in ingredients:
        Ingredient.objects.get_or_create(name=name)

    print(f"✅ Seeded {len(skin_types)} SkinType, {len(concerns)} Concern, {len(tags)} Tag, {len(ingredients)} Ingredient.")

def import_products(csv_path):
    """محصولات را بساز و روابط M2M را ست کن."""
    with open(csv_path, encoding='utf-8') as f:
        reader = csv.DictReader(f)

        for row in reader:
            # 1) ایجاد یا بارگذاری محصول (بدون M2M)
            prod, created = Product.objects.get_or_create(
                id=row['id'],
                defaults={
                    'name': row['name'],
                    'brand': row['brand'],
                    'category': row['category'],
                    'price': row['price'] or 0,
                    'rating': 0.0,
                    'rate_quantity': 0,
                    'image_url': row.get('image_url', ''),
                    'quantity': 0,
                    'sold_quantity': 0,
                }
            )

            # 2) ست کردن روابط M2M با .set()
            # skin_type
            st_objs = []
            for name in row.get('skin_types','').split(';'):
                name = name.strip()
                if not name: continue
                obj = SkinType.objects.get(name=name)
                st_objs.append(obj)
            prod.skin_type.set(st_objs)

            # concerns_targeted
            c_objs = []
            for name in row.get('concerns_targeted','').split(';'):
                name = name.strip()
                if not name: continue
                obj = Concern.objects.get(name=name)
                c_objs.append(obj)
            prod.concerns_targeted.set(c_objs)

            # tags
            t_objs = []
            for name in row.get('tags','').split(';'):
                name = name.strip()
                if not name: continue
                obj = Tag.objects.get(name=name)
                t_objs.append(obj)
            prod.tags.set(t_objs)

            # ingredients
            i_objs = []
            for name in row.get('ingredients','').split(';'):
                name = name.strip()
                if not name: continue
                obj = Ingredient.objects.get(name=name)
                i_objs.append(obj)
            prod.ingredients.set(i_objs)

            print(f"{'Created' if created else 'Updated'}: {prod.name}")

if __name__ == '__main__':
    # اگر قبلاً مایگریت نکرده‌اید اطمینان حاصل کنید که مدل‌های M2M در دیتابیس وجود دارند.
    seed_m2m_values(CSV_PATH)
    import_products(CSV_PATH)
