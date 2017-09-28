from django.db import models

# Create your models here.
class tlgbot(models.Model):
    auth = models.ForeignKey('auth.User')
    botName = models.CharField(max_length=200)
    botUserName = models.CharField(max_length=200)
    botURL = models.CharField(max_length=500)
    botToken = models.CharField(max_length=200)

    def __str__(self):
        return self.botName