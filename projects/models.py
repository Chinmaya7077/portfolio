from django.db import models


class Project(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    subtitle = models.CharField(max_length=300, blank=True)
    description = models.TextField()
    role = models.CharField(max_length=300, blank=True)
    tech_stack = models.CharField(max_length=500, help_text="Comma-separated")
    highlights = models.TextField(blank=True, help_text="One per line")
    order = models.IntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title

    def tech_list(self):
        return [t.strip() for t in self.tech_stack.split(',') if t.strip()]

    def highlight_list(self):
        return [h.strip() for h in self.highlights.split('\n') if h.strip()]
