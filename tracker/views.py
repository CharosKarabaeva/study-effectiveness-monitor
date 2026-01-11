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

    # =========================
    # ОБЩАЯ ОЦЕНКА СОСТОЯНИЯ
    # =========================
    if avg_productivity >= 4:
        recommendations.append({
            'type': 'success',
            'icon': '🟢',
            'text': (
                "В целом наблюдается высокий уровень учебной продуктивности. "
                "Текущий учебный режим можно считать эффективным."
            )
        })
    elif avg_productivity <= 2.5:
        recommendations.append({
            'type': 'danger',
            'icon': '🔴',
            'text': (
                "Средний уровень учебной продуктивности находится на низком уровне. "
                "Рекомендуется пересмотреть организацию учебного процесса."
            )
        })
    else:
        recommendations.append({
            'type': 'info',
            'icon': '🔵',
            'text': (
                "Учебная продуктивность находится на среднем уровне. "
                "Существует потенциал для её повышения."
            )
        })

    # =========================
    # НАСТРОЕНИЕ + ПРОДУКТИВНОСТЬ
    # =========================
    if avg_mood >= 4 and avg_productivity < 3.5:
        recommendations.append({
            'type': 'warning',
            'icon': '🟡',
            'text': (
                "Несмотря на положительное эмоциональное состояние, уровень продуктивности остаётся невысоким. "
                "Возможно, проблема связана с планированием или отвлекающими факторами."
            )
        })

    if avg_mood >= 4 and avg_productivity >= 4:
        recommendations.append({
            'type': 'success',
            'icon': '✨',
            'text': (
                "Положительное настроение способствует высокой учебной эффективности. "
                "Рекомендуется планировать сложные задачи на такие периоды."
            )
        })

    # =========================
    # УСТАЛОСТЬ + ПРОДУКТИВНОСТЬ
    # =========================
    if avg_fatigue >= 4 and avg_productivity >= 3:
        recommendations.append({
            'type': 'warning',
            'icon': '⚠️',
            'text': (
                "Высокая усталость сочетается с сохранением продуктивности. "
                "Это может указывать на риск переутомления."
            )
        })

    if avg_fatigue >= 4 and avg_productivity < 3:
        recommendations.append({
            'type': 'danger',
            'icon': '😴',
            'text': (
                "Повышенная усталость негативно влияет на учебную эффективность. "
                "Рекомендуется сократить нагрузку и уделить внимание восстановлению."
            )
        })

    # =========================
    # АНАЛИЗ ДИНАМИКИ
    # =========================
    if len(productivities) >= 4:
        last = productivities[-4:]

        if last == sorted(last):
            recommendations.append({
                'type': 'success',
                'icon': '📈',
                'text': (
                    "Отмечается положительная динамика учебной продуктивности за последние дни. "
                    "Текущий подход к обучению даёт хорошие результаты."
                )
            })

        if last == sorted(last, reverse=True):
            recommendations.append({
                'type': 'danger',
                'icon': '📉',
                'text': (
                    "Наблюдается устойчивая тенденция к снижению продуктивности. "
                    "Рекомендуется скорректировать учебный режим."
                )
            })

    # =========================
    # НЕСТАБИЛЬНОСТЬ
    # =========================
    if max(productivities) - min(productivities) >= 3:
        recommendations.append({
            'type': 'info',
            'icon': '🔄',
            'text': (
                "Учебная продуктивность характеризуется резкими колебаниями. "
                "Рекомендуется стабилизировать расписание и нагрузку."
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