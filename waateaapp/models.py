from django.db import models
from waateax.users.models import User
import uuid
# Create your models here.
class MotherModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class Club(MotherModel):
    name = models.CharField(max_length=200)
    ordering = ['name']

    def __str__(self):
        return self.name

class Team(MotherModel):
    name = models.CharField(max_length=200)
    club = models.ForeignKey(Club, on_delete=models.CASCADE,blank=True,null=True)

    ordering = ['club', 'name']

    def __str__(self):
        return self.name

class Season(MotherModel):
    name = models.CharField(max_length=200)

    ordering = ['name']

    def __str__(self):
        return self.name



class Game(MotherModel):
    home = models.ForeignKey(Club, related_name='home_team', on_delete=models.CASCADE,blank=True,null=True)
    away = models.ForeignKey(Club, related_name='away_team', on_delete=models.CASCADE,blank=True,null=True)
    team = models.ForeignKey(Team, on_delete=models.CASCADE,blank=True,null=True)
    season = models.ForeignKey(Season, on_delete=models.CASCADE,blank=True,null=True)
    time = models.TimeField(null=True,blank=True)

    ordering = ['date']

    def __str__(self):
        return f"{self.home} - {self.away}"


class Gameday(MotherModel):
    season = models.ForeignKey(Season, on_delete=models.CASCADE,blank=True,null=True)
    date = models.DateField(null=True,blank=True)
    games = models.ManyToManyField(Game)

    ordering = ['date']

    def __str__(self):
        return f"{self.date} - {self.season} - {self.games}"

class Availbility(MotherModel):
    STATE_CHOICES=[
        (0, 'Not set'),
        (1, 'Dont know'),
        (2, 'Unavailable'),
        (3, 'Available'),
    ]

    gameday = models.ForeignKey(Gameday, on_delete=models.CASCADE,blank=True,null=True)
    player = models.ForeignKey(User, on_delete=models.CASCADE)
    state = models.IntegerField(choices=STATE_CHOICES,default=0)

    ordering = ['name']

    def __str__(self):
        return f"{self.gameday}"
