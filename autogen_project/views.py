from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import Event
from django.views.decorators.csrf import csrf_exempt
import json


def calendar_view(request):
    return render(request, 'calendar.html')


def events_api(request):
    # Return all events as JSON for calendar
    events = Event.objects.all()
    events_list = []
    for event in events:
        events_list.append({
            'id': event.id,
            'title': event.title,
            'start': event.start_time.isoformat(),
            'end': event.end_time.isoformat(),
            'color': event.color,
        })
    return JsonResponse(events_list, safe=False)


def event_detail_api(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    data = {
        'id': event.id,
        'title': event.title,
        'description': event.description,
        'start': event.start_time.isoformat(),
        'end': event.end_time.isoformat(),
        'color': event.color,
    }
    return JsonResponse(data)
