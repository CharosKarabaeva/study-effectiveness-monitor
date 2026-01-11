from django.shortcuts import render, redirect
from django.db.models import Avg
from django.http import JsonResponse

from .models import StudyDay
from .forms import StudyDayForm

# =========================
# СПИСОК УЧЕБНЫХ ДНЕЙ + ФОРМА + ФИЛЬТР
# =========================
def study_days_list(request):
    # ---------- ФОРМА ----------
    if request.method == 'POST':
        form = StudyDayForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('study_days_list')
    else:
        form = StudyDayForm()

    # ---------- ФИЛЬТР ----------
    days_qs = StudyDay.objects.all()

    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')

    if date_from and date_to:
        days_qs = days_qs.filter(date__range=[date_from, date_to])

    days = list(days_qs.order_by('date'))

    # ---------- СРЕДНИЕ ----------
    averages = days_qs.aggregate(
        avg_productivity=Avg('productivity'),
        avg_mood=Avg('mood'),
        avg_fatigue=Avg('fatigue'),
    )

    # ---------- ВЛИЯНИЕ НАСТРОЕНИЯ ----------
    mood_stats = (
        days_qs
        .values('mood')
        .annotate(avg_productivity=Avg('productivity'))
        .order_by('mood')
    )

    # ---------- ВЛИЯНИЕ УСТАЛОСТИ ----------
    fatigue_stats = (
        days_qs
        .values('fatigue')
        .annotate(avg_productivity=Avg('productivity'))
        .order_by('fatigue')
    )

    # ---------- РЕКОМЕНДАЦИИ ----------
    recommendations = generate_recommendations(days)

    return render(
        request,
        'tracker/study_days_list.html',
        {
            'days': days,
            'form': form,
            'averages': averages,
            'mood_stats': mood_stats,
            'fatigue_stats': fatigue_stats,
            'recommendations': recommendations,
        }
    )


# =========================
# РЕКОМЕНДАТЕЛЬНАЯ СИСТЕМА
# =========================
def generate_recommendations(days):
    recommendations = []

    if not days:
        return [{
            'type': 'info',
            'icon': 'ℹ️',
            'text': 'Недостаточно данных для формирования рекомендаций.'
        }]

    moods = [d.mood for d in days]
    fatigues = [d.fatigue for d in days]
    productivities = [d.productivity for d in days]

    avg_mood = sum(moods) / len(moods)
    avg_fatigue = sum(fatigues) / len(fatigues)
    avg_productivity = sum(productivities) / len(productivities)

    # Позитив
    if avg_mood >= 4 and avg_productivity >= 4:
        recommendations.append({
            'type': 'success',
            'icon': '🟢',
            'text': (
                "Высокий уровень настроения положительно влияет на учебную продуктивность. "
                "Рекомендуется планировать сложные задания на такие дни."
            )
        })

    # Усталость
    if avg_fatigue >= 4 and avg_productivity <= 3:
        recommendations.append({
            'type': 'warning',
            'icon': '🟡',
            'text': (
                "Повышенная усталость сопровождается снижением эффективности обучения. "
                "Рекомендуется сократить нагрузку и предусмотреть отдых."
            )
        })

    # Колебания
    if max(productivities) - min(productivities) >= 2:
        recommendations.append({
            'type': 'info',
            'icon': '🔵',
            'text': (
                "Отмечаются значительные колебания уровня продуктивности. "
                "Рекомендуется стабилизировать режим обучения."
            )
        })

    # Падение продуктивности
    if len(productivities) >= 3:
        last_three = productivities[-3:]
        if last_three[0] > last_three[1] > last_three[2]:
            recommendations.append({
                'type': 'danger',
                'icon': '🔴',
                'text': (
                    "Наблюдается последовательное снижение продуктивности за последние дни. "
                    "Рекомендуется пересмотреть учебный график."
                )
            })

    # Если всё ок
    if not recommendations:
        recommendations.append({
            'type': 'success',
            'icon': '✅',
            'text': (
                "Выраженных негативных тенденций не выявлено. "
                "Рекомендуется продолжать текущий режим обучения."
            )
        })

    return recommendations


# =========================
# API ДЛЯ CHART.JS
# =========================
def analytics_data(request):
    days_qs = StudyDay.objects.all()

    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')

    if date_from and date_to:
        days_qs = days_qs.filter(date__range=[date_from, date_to])

    days = list(days_qs.order_by('date'))

    return JsonResponse({
        'dates': [d.date.strftime('%Y-%m-%d') for d in days],
        'mood': [d.mood for d in days],
        'fatigue': [d.fatigue for d in days],
        'productivity': [d.productivity for d in days],
    })