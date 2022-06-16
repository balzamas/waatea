from django.contrib import admin

from .models import Club, Team, Availbility, Season, Game, Gameday

# Register your models here.
admin.site.register(Club)
admin.site.register(Team)
admin.site.register(Season)

class GameAdmin(admin.ModelAdmin):
    list_display = ['home', 'away', 'team', 'season', 'get_date']
    ordering = ['team']
    list_filter = ('season', 'team')

    def get_date(self, obj):
        gamedays = Gameday.objects.filter(games=obj)
        if gamedays:
            return gamedays[0].date
        else:
            return "-"

    get_date.short_description = 'Date'

admin.site.register(Game, GameAdmin)

class AvailabilityAdmin(admin.ModelAdmin):
    list_display = ['player', 'gameday', 'state']
    ordering = ['gameday__date', 'player', 'state']
    list_filter = ('player', 'gameday', 'state')

admin.site.register(Availbility, AvailabilityAdmin)


class GamedayAdmin(admin.ModelAdmin):
    list_display = ['date', 'season']
    ordering = ['season', 'date']
    list_filter = ('season', 'date')

admin.site.register(Gameday, GamedayAdmin)
