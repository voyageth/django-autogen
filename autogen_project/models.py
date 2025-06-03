from django.db import models

class Event(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    color = models.CharField(max_length=7, default='#3788d8')  # HEX color code

    def __str__(self):
        return self.title
