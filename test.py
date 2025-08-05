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

from products.models import Product

CSV_PATH = os.path.join(PROJECT_ROOT, 'products_1000.csv')

def import_products(csv_path):
    products = []
    with open(csv_path, encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            products.append(Product(
                id=row['id'],
                name=row['name'],
                brand=row['brand'],
                category=row['category'],
                skin_type=row.get('skin_types', ''),
                concerns_targeted=row.get('concerns_targeted', ''),
                ingredients=row.get('ingredients', ''),
                tags=row.get('tags', ''),
                price=row['price'] or 0,
                rating=0.0,
                rate_quantity=0,
                image_url=row.get('image_url', ''),
                quantity=0,
                sold_quantity=0,
            ))

    # (اختیاری) پاک کردن همهٔ محصولات قبلی
    # Product.objects.all().delete()

    # واردسازی دسته‌جمعی
    Product.objects.bulk_create(products, batch_size=200)
    print(f"✅ Imported {len(products)} products.")

if __name__ == '__main__':
    import_products('products_1000.csv')
