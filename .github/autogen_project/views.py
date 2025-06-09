from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import Event


def calendar_view(request):
    """캘린더 페이지 렌더링"""
    return render(request, "calendar.html")


def events_api(request):
    """모든 일정을 JSON으로 반환"""
    events = Event.objects.all()
    data = [
        {
            "id": e.id,
            "title": e.title,
            "start": e.start_time.isoformat(),
            "end": e.end_time.isoformat(),
            "color": e.color,
        }
        for e in events
    ]
    return JsonResponse(data, safe=False)


def event_detail_api(request, event_id):
    """특정 일정 상세 정보를 JSON으로 반환"""
    event = get_object_or_404(Event, pk=event_id)
    data = {
        "id": event.id,
        "title": event.title,
        "description": event.description,
        "start": event.start_time.isoformat(),
        "end": event.end_time.isoformat(),
        "color": event.color,
    }
    return JsonResponse(data)
