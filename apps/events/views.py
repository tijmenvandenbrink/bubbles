from django.shortcuts import render


def events_list(request):
    return render(request, 'events.html', {"active": "events"})