import os
import django

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")
django.setup()

from products.models import ProductColorImage

updated_count = 0
skipped_count = 0

for img in ProductColorImage.objects.all():
    image_name = img.image.name  # e.g., 'media/1_tu0uug_avkcrw' or '1_tu0uug_avkcrw'

    if image_name.startswith("media/"):
        new_name = image_name.replace("media/", "", 1)  # remove only first occurrence
        img.image.name = new_name
        img.save(update_fields=["image"])
        updated_count += 1
        print(f"Updated [{img.id}]: '{image_name}' -> '{new_name}'")
    else:
        skipped_count += 1
        print(f"Skipped [{img.id}]: '{image_name}' already clean")

print(f"\n✅ Total updated: {updated_count}")
print(f"⏭️ Total skipped (already clean): {skipped_count}")
