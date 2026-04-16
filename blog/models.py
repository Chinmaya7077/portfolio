from django.db import models
from django.utils.text import slugify
import markdown
from markdown.extensions.codehilite import CodeHiliteExtension
from markdown.extensions.fenced_code import FencedCodeExtension


class Post(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    excerpt = models.CharField(max_length=400, blank=True)
    content = models.TextField(help_text="Write in Markdown")
    published = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def content_html(self):
        md = markdown.Markdown(extensions=[
            FencedCodeExtension(),
            CodeHiliteExtension(css_class='codehilite', linenums=False),
            'tables',
        ])
        return md.convert(self.content)

    def reading_time(self):
        words = len(self.content.split())
        return max(1, round(words / 200))
