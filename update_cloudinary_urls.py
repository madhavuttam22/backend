# update_cloudinary_urls.py
import os
import django
import cloudinary
import cloudinary.api

# Django setup
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")  # your settings module
django.setup()

from products.models import ProductColorImage  # your model

# Cloudinary config
cloudinary.config(
    cloud_name='drrxzryrl',
    api_key='298414175445982',
    api_secret='V-_ezwXd0kZQt9rIC8xuNbPXmP4'
)

# Fetch all uploaded images from Cloudinary
resources = cloudinary.api.resources(type='upload', max_results=500)['resources']

# Prepare lookup: old base ID -> new URL
lookup = {}
for res in resources:
    # res['public_id'] example: "media/product_color_images/1_tu0uug_u4rmld"
    public_id = res['public_id'].split('/')[-1]  # "1_tu0uug_u4rmld"
    base_id = '_'.join(public_id.split('_')[:2])  # "1_tu0uug"
    lookup[base_id] = res['secure_url']  # full Cloudinary URL

# Update database
for image in ProductColorImage.objects.all():
    # old URL / old file name
    old_filename = image.image.name.split('/')[-1].split('.')[0]  # "1_tu0uug"
    if old_filename in lookup:
        # get the public_id from Cloudinary URL
        new_url = lookup[old_filename]  # e.g., "https://res.cloudinary.com/drrxzryrl/image/upload/v1757852817/1_tu0uug_u4rmld.webp"
        # Extract relative path after /upload/
        path_index = new_url.find('/upload/') + len('/upload/')
        relative_path = new_url[path_index:]  # "v1757852817/1_tu0uug_u4rmld.webp"

        # assign to ImageField
        image.image.name = relative_path
        image.save()
        print(f"Updated {image.id} -> {relative_path}")



print("All images updated successfully!")
