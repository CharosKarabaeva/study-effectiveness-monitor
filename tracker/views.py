from django.shortcuts import render, redirect
from django.db.models import Avg
from .models import StudyDay
from .forms import StudyDayForm

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os
from django.conf import settings


def study_days_list(request):
    if request.method == 'POST':
        form = StudyDayForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('study_days_list')
    else:
        form = StudyDayForm()

    days = StudyDay.objects.all().order_by('date')

    from django.db.models import Avg

    averages = StudyDay.objects.aggregate(
        avg_productivity=Avg('productivity'),
        avg_mood=Avg('mood'),
        avg_fatigue=Avg('fatigue'),
    )

    # Анализ влияния настроения
    mood_stats = (
        StudyDay.objects
        .values('mood')
        .annotate(avg_productivity=Avg('productivity'))
        .order_by('mood')
    )

    # Анализ влияния усталости
    fatigue_stats = (
        StudyDay.objects
        .values('fatigue')
        .annotate(avg_productivity=Avg('productivity'))
        .order_by('fatigue')
    )

    # --- График ---
    dates = [day.date for day in days]
    productivity = [day.productivity for day in days]

    plt.figure()
    plt.plot(dates, productivity, marker='o')
    plt.title('Продуктивность по дням')
    plt.xlabel('Дата')
    plt.ylabel('Продуктивность')
    plt.grid(True)

    static_dir = os.path.join(settings.BASE_DIR, 'static')
    os.makedirs(static_dir, exist_ok=True)
    chart_path = os.path.join(static_dir, 'productivity_chart.png')

    plt.savefig(chart_path)
    plt.close()

    return render(
        request,
        'tracker/study_days_list.html',
        {
            'days': days,
            'averages': averages,
            'chart_url': 'productivity_chart.png',
            'form': form,
            'mood_stats': mood_stats,
            'fatigue_stats': fatigue_stats,
        }
    )
