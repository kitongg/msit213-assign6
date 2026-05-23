from django.db import models
from django.conf import settings

class Album(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name='albums')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('albums:album-detail', args=[str(self.pk)])

class Photo(models.Model):
    album = models.ForeignKey(Album, on_delete=models.CASCADE, related_name='photos')
    title = models.CharField(max_length=200, blank=True)
    image = models.ImageField(upload_to='photos/')
    image_webp = models.ImageField(upload_to='photos/', blank=True, null=True)
    thumbnail = models.ImageField(upload_to='photos/thumbs/', blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return self.title or f'Photo {self.pk}'

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('albums:album-detail', args=[str(self.album.pk)])

    def save(self, *args, **kwargs):
        # Save original first
        super().save(*args, **kwargs)

        # Generate webp and thumbnail using Pillow
        try:
            from PIL import Image
            from io import BytesIO
            from django.core.files.base import ContentFile
            import os

            if self.image and (not self.image_webp):
                img_path = self.image.path
                im = Image.open(img_path).convert('RGB')
                webp_io = BytesIO()
                im.save(webp_io, format='WEBP', quality=85)
                webp_name = os.path.splitext(os.path.basename(self.image.name))[0] + '.webp'
                self.image_webp.save(webp_name, ContentFile(webp_io.getvalue()), save=False)

            if self.image and (not self.thumbnail):
                img_path = self.image.path
                im = Image.open(img_path)
                im.thumbnail((800, 800))
                thumb_io = BytesIO()
                format = 'JPEG' if im.mode in ('RGB', 'L', 'P') else 'PNG'
                im.save(thumb_io, format=format, quality=85)
                thumb_name = os.path.splitext(os.path.basename(self.image.name))[0] + '_thumb.jpg'
                self.thumbnail.save(thumb_name, ContentFile(thumb_io.getvalue()), save=False)

            # Save again to persist generated files
            super().save(*args, **kwargs)
        except Exception:
            # If Pillow or storage not available, skip generation silently
            pass
