from django.shortcuts import render
from waateaapp.models import Gameday, Availbility
from django.http import HttpResponse
from django.views.generic import TemplateView
from waateax.users.models import User

class game_index(TemplateView):
    model = Gameday
    template_name = "pages/join.html"

    def getgamelist(self):

        print(self.request.user)

        for gameday in Gameday.objects.all():
                check = Availbility.objects.filter(gameday=gameday, player=self.request.user)
                if check.count() == 0:
                    print("Create Record")
                    check = Availbility(gameday=gameday, player=self.request.user)
                    check.save()


        return Availbility.objects.filter(player=self.request.user)


class list_index(TemplateView):
    model = User
    template_name = "pages/list.html"

    def generatetable(self):
        table = {}
        html = "<table style='border: 1px solid black'><tr style='border: 1px solid black'><th></th>"
        gamedays = Gameday.objects.all().order_by('date')
        for gameday in gamedays:
            html += f"<th></th><th style='text-align:center'>{gameday.date}"
            for game in gameday.games.all():
                html += f"<br>{game.home} - {game.away}"


            dontknow = Availbility.objects.filter(gameday=gameday, state=1)
            no = Availbility.objects.filter(gameday=gameday, state=2)
            yes = Availbility.objects.filter(gameday=gameday, state=3)
            notset = User.objects.filter(active=True).count() - dontknow.count() - no.count() - yes.count()
            html += "<p>"
            html += f'<p style="color:black">Not set: {notset}</p>'
            html += f'<p style="color:orange">Not sure: {dontknow.count()}</p>'
            html += f'<p style="color:red">No: {no.count()}</p>'
            html += f'<p style="color:green">Yes!: {yes.count()}</p>'
            html += "</p>"

            html += "</th>"
        html += "</tr>"

        for player in User.objects.filter(active=True):
            html += f"<tr style='border: 1px solid black'><td>{player.name} </td>"


            for gameday in Gameday.objects.all().order_by('date'):
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
