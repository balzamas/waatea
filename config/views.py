from django.shortcuts import render
from waateaapp.models import Gameday, Availbility
from django.http import HttpResponse
from django.views.generic import TemplateView
from waateax.users.models import User
from django.template import loader
from datetime import date
import csv

def create_csv_gameday(request, gameday_id):
    gameday = Gameday.objects.get(id=gameday_id)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="gameday.csv"'
    writer = csv.writer(response)

    update_availlist(gameday)

    avail_list = Availbility.objects.filter(gameday=gameday, player__active=True).order_by('player__name')

    writer.writerow([gameday.date])
    for game in gameday.games.all():
        writer.writerow([f"{game.home} vs {game.away}", f"{game.team}"])
    writer.writerow([])
    writer.writerow(["Name", "State", "Last update"])

    for avail in avail_list:
        writer.writerow([avail.player.name, avail.state, avail.updated])

    writer.writerow([])
    writer.writerow(["0 = Not Set"])
    writer.writerow(["1 = Don't know"])
    writer.writerow(["2 = Unavailable"])
    writer.writerow(["3 = Available"])

    return response

def calc_avail_totals(gameday):
    dontknow = Availbility.objects.filter(gameday=gameday, player__active=True, state=1)
    no = Availbility.objects.filter(gameday=gameday, player__active=True, state=2)
    yes = Availbility.objects.filter(gameday=gameday, player__active=True, state=3)
    notset = User.objects.filter(active=True).count() - dontknow.count() - no.count() - yes.count()
    return dontknow, no, yes, notset

def update_availlist(gameday):
    for player in User.objects.filter(active=True).order_by('name'):
        update_availlist_player(gameday, player)

def update_availlist_player(gameday,player):
        check = Availbility.objects.filter(gameday=gameday, player=player)

        if check.count() == 0:
            print("Create Record")
            check = Availbility(gameday=gameday, player=player)
            check.save()

def game(request, gameday_id):
    gameday = Gameday.objects.get(id=gameday_id)
    games = gameday.games.all()
    whatsapp_text=f"?text=Are%20you%20available%20for%20{gameday.date}?%20Please%20update%20Waatea!"

    dontknow, no, yes, notset = calc_avail_totals(gameday)
    html = ""
    html += "<p>"
    html += f'<div style="color:black">Not set: {notset}</div>'
    html += f'<div style="color:orange">Not sure: {dontknow.count()}</div>'
    html += f'<div style="color:red">No: {no.count()}</div>'
    html += f'<div style="color:green">Yes!: {yes.count()}</div>'
    html += "</p>"

    update_availlist(gameday)

    avail = Availbility.objects.filter(gameday=gameday, player__active=True).order_by('player__name')

    template = loader.get_template('pages/game.html')
    context = {
        'games': games,
        'gameday': gameday,
        'availability': avail,
        'whatsapp_text':whatsapp_text,
        'totals' : html
    }
    return HttpResponse(template.render(context, request))

class game_index(TemplateView):
    model = Gameday
    template_name = "pages/game.html"

    def getgamelist(self):

        print(self.request.user)

        for gameday in Gameday.objects.all():
                check = Availbility.objects.filter(gameday=gameday, player=self.request.user)
                if check.count() == 0:
                    print("Create Record")
                    check = Availbility(gameday=gameday, player=self.request.user)
                    check.save()


        return Availbility.objects.filter(player=self.request.user).order_by('gameday__date')


class join_index(TemplateView):
    model = Gameday
    template_name = "pages/join.html"

    def getgamelist(self):
        print(self.request.user)

        for gameday in Gameday.objects.filter(date__gte=date.today()).order_by('date'):
            update_availlist_player(gameday,self.request.user)

        return Availbility.objects.filter(player=self.request.user,gameday__date__gte=date.today()).order_by('gameday__date')

class list_index(TemplateView):
    model = User
    template_name = "pages/list.html"

    def generatetable(self):
        table = {}
        html = "<table style='border: 1px solid black'><tr style='border: 1px solid black'><th></th>"
        gamedays = Gameday.objects.filter(date__gte=date.today()).order_by('date')
        for gameday in gamedays:
            html += f"<th></th><th style='text-align:center'>{gameday.date}"
            for game in gameday.games.all():
                html += f"<br>{game.home} - {game.away}"

            dontknow, no, yes, notset = calc_avail_totals(gameday)
            html += "<p>"
            html += f'<p style="color:black">Not set: {notset}</p>'
            html += f'<p style="color:orange">Not sure: {dontknow.count()}</p>'
            html += f'<p style="color:red">No: {no.count()}</p>'
            html += f'<p style="color:green">Yes!: {yes.count()}</p>'
            html += "</p>"

            html += "</th>"
        html += "</tr>"

        for player in User.objects.filter(active=True).order_by('name'):
            html += f"<tr style='border: 1px solid black'><td>{player.name} </td>"


            for gameday in Gameday.objects.filter(date__gte=date.today()).order_by('date'):
                avail_ = Availbility.objects.filter(player=player,gameday=gameday)
                html +="<td>&nbsp;&nbsp;&nbsp;</td>"
                if (avail_.count() == 0):
                    html += f"<td style='text-align:center'><i class='hourglass half icon'></td>"
                else:
                    icon = ""
                    whatsapptext=f"?text=Are%20you%20available%20for%20{gameday.date}?%20Please%20update%20Waatea!"
                    if avail_[0].state == 0:
                        icon = f'<i class="hourglass half icon"></i>&nbsp<a href="https://wa.me/{player.mobile_phone}{whatsapptext}" target="_blank"><i class="whatsapp icon"></a>'
                    if avail_[0].state == 1:
                        icon = f'<i class="orange question circle icon"></i>&nbsp<a href="https://wa.me/{player.mobile_phone}{whatsapptext}" target="_blank"><i class="whatsapp icon"></a>'
                    if avail_[0].state == 2:
                        icon = f'<i class="red thumbs down icon"></i>'
                    if avail_[0].state == 3:
                        icon = f'<i class="green thumbs up icon"></i>'

                    html += f"<td style='text-align:center'>{icon}</td>"


            html += f"</tr>"

        html += "</table>"

        return html

class gamedays_index(TemplateView):
    model = Gameday
    template_name = "pages/gamedays.html"

    def generatetable(self):
        html = ""

        gamedays = Gameday.objects.filter(date__gte=date.today()).order_by('date')
        for gameday in gamedays:
            html += f'<a href="/gameday/{gameday.id}">'
            html += '<div class ="item">'
            html += '<div class="row">'
            html += '<div class="column70">'
            html += f"<p><b>{gameday.date}</b></p>"
            for game in gameday.games.all():
                html += f"<p>{game.home} - {game.away}<br>({game.team})</p>"

            dontknow, no, yes, notset = calc_avail_totals(gameday)
            html += '</div>'
            html += '<div class="column30">'

            html += f'<div style="color:black">Not set: {notset}</div>'
            html += f'<div style="color:orange">Not sure: {dontknow.count()}</div>'
            html += f'<div style="color:red">No: {no.count()}</div>'
            html += f'<div style="color:green">Yes!: {yes.count()}</div>'
            html += '</div>'
            html += '</div>'
            html += '</a></div>'
            html += '<div class ="break"> </div>'


        return html


def toggleavail(request):
    if request.method == 'GET':
        post_id = request.GET['post_id']
        post_value = request.GET['post_value']
        likedpost = Availbility.objects.get(id = post_id )
        likedpost.state=post_value
        likedpost.save()
        return HttpResponse('success')
    else:
        return HttpResponse("unsuccesful")
