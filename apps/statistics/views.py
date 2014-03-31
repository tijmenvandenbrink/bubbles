from django.shortcuts import render


def statistics_list(request):
    return render(request, 'statistics.html', {"active": "statistics"})