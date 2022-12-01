
from django.utils import timezone
from django.shortcuts import render,redirect
from django.http import HttpResponse,Http404
from django import forms
from django.core.exceptions import ValidationError

from django_user_agents.utils import get_user_agent

from string import ascii_letters,digits
from random import choice
from datetime import timedelta
from .models import Url,Click


def index(request):
    urls = Url.objects.order_by('-created_at')
    context = {'urls': urls}
    return render(request, 'heyurl/index.html', context)

def store(request):
    # FIXME: Insert a new URL object into storage

    full_url = request.POST.get("original_full_url")
    valid_url = forms.URLField()

    try:
        valid_url.clean(full_url)
    except ValidationError:
        return HttpResponse("INVALID URL")
    else:

        if Url.objects.filter(original_url = full_url).exists() == False:

            while True:
                short_url = ''.join(choice(ascii_letters+digits) for a in range(5))
                if Url.objects.filter(short_url = short_url).exists() == False:
                    Url(short_url = short_url,original_url = full_url, created_at = timezone.now(), updated_at=timezone.now()).save()
                    return HttpResponse("Storing a new URL object into storage")
        else:
            return HttpResponse("INVALID URL")



   
def short_url(request, short_url):
    # FIXME: Do the logging to the db of the click with the user agent and browser

    try:
        short_url_exist = Url.objects.get(short_url = short_url)
    except Url.DoesNotExist:
        raise Http404("SHORT URL DOESN'T EXIST")
    else:

        browser = ''
        plataform = ''

        if request.user_agent.is_mobile:
            plataform = "mobile"
        elif request.user_agent.is_tablet:
            plataform = "tablet"
        elif request.user_agent.is_touch_capable:
            plataform = "touch_capable"
        elif request.user_agent.is_pc:
            plataform = "pc"
        elif request.user_agent.is_bot:
            plataform = "bot"

        browser = request.user_agent.browser.family

        short_url_exist.clicks += 1
        short_url_exist.save()

        print(browser)
        print(plataform)

        Click(url = short_url_exist , browser = browser, platform = plataform, created_at = timezone.now()-timedelta(days=2),updated_at= timezone.now() ).save()

        # return HttpResponse("You're looking at url %s" % short_url)
        return redirect(short_url_exist.original_url)

def metrics(request, short_url):


    click_info =  Click.objects.filter(url__short_url = short_url, created_at__month = timezone.now().month)

    click_per_day ={}
    click_per_browser ={}
    click_per_plataform = {}


    for click in click_info:

        if click.created_at.day in click_per_day.keys():
            click_per_day[click.created_at.day] += 1
        else:
            click_per_day[click.created_at.day] = 1

        if click.browser in click_per_browser.keys():
            click_per_browser[click.browser] += 1
        else:
            click_per_browser[click.browser] = 1

        if click.platform in click_per_plataform.keys():
            click_per_plataform[click.platform] += 1
        else:
            click_per_plataform[click.platform] = 1

    
    context = {'clicks_per_day': sorted(click_per_day.items()),'clicks_per_browser': sorted(click_per_browser.items()), 'clicks_per_plataform':sorted(click_per_plataform.items()) }
    return render(request, "heyurl/metrics.html",context)

