from django.shortcuts import render, redirect
from django.db.models import Avg
from django.http import JsonResponse

from .models import StudyDay
from .forms import StudyDayForm


# =========================
# СПИСОК УЧЕБНЫХ ДНЕЙ + ФОРМА
# =========================
def study_days_list(request):
    # Обработка формы
    if request.method == 'POST':
        form = StudyDayForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('study_days_list')
    else:
        form = StudyDayForm()

    # Данные
    days = list(StudyDay.objects.all().order_by('date'))

    # Средние значения
    averages = StudyDay.objects.aggregate(
        avg_productivity=Avg('productivity'),
        avg_mood=Avg('mood'),
        avg_fatigue=Avg('fatigue'),
    )

    # Влияние настроения
    mood_stats = (
        StudyDay.objects
        .values('mood')
        .annotate(avg_productivity=Avg('productivity'))
        .order_by('mood')
    )

    # Влияние усталости
    fatigue_stats = (
        StudyDay.objects
        .values('fatigue')
        .annotate(avg_productivity=Avg('productivity'))
        .order_by('fatigue')
    )

    # Рекомендации
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
    """
    Формирует текстовые рекомендации на основе
    анализа учебной продуктивности и
    психоэмоциональных параметров.
    """

    recommendations = []

    if not days:
        return recommendations

    moods = [d.mood for d in days]
    fatigues = [d.fatigue for d in days]
    productivities = [d.productivity for d in days]

    avg_mood = sum(moods) / len(moods)
    avg_fatigue = sum(fatigues) / len(fatigues)
    avg_productivity = sum(productivities) / len(productivities)

    # 1. Высокое настроение и высокая продуктивность
    if avg_mood >= 4 and avg_productivity >= 4:
        recommendations.append(
            "Высокий уровень настроения положительно влияет на учебную продуктивность. "
            "Рекомендуется планировать наиболее сложные задания на такие дни."
        )

    # 2. Высокая усталость и низкая продуктивность
    if avg_fatigue >= 4 and avg_productivity <= 3:
        recommendations.append(
            "Повышенный уровень усталости сопровождается снижением эффективности обучения. "
            "Рекомендуется сократить нагрузку и предусмотреть дополнительный отдых."
        )

    # 3. Нестабильная продуктивность
    if max(productivities) - min(productivities) >= 2:
        recommendations.append(
            "Отмечаются значительные колебания уровня продуктивности. "
            "Рекомендуется стабилизировать режим обучения и отдыха."
        )

    # 4. Снижение продуктивности в последние дни
    if len(productivities) >= 3:
        last_three = productivities[-3:]
        if last_three[0] > last_three[1] > last_three[2]:
            recommendations.append(
                "Наблюдается последовательное снижение продуктивности за последние учебные дни. "
                "Возможно, требуется пересмотр учебного графика."
            )

    # 5. Общая низкая продуктивность
    if avg_productivity <= 2.5:
        recommendations.append(
            "Средний уровень учебной продуктивности остаётся низким. "
            "Рекомендуется обратить внимание на режим сна и восстановление."
        )

    # Если рекомендаций нет — нейтральный вывод
    if not recommendations:
        recommendations.append(
            "На данный момент выраженных негативных или позитивных тенденций не выявлено. "
            "Рекомендуется продолжать наблюдение за учебной активностью."
        )

    return recommendations


# =========================
# СТРАНИЦА АНАЛИТИКИ (Chart.js)
# =========================
def analytics_page(request):
    days = list(StudyDay.objects.all().order_by('date'))
    recommendations = generate_recommendations(days)

    return render(
        request,
        'tracker/analytics_chartjs.html',
        {
            'recommendations': recommendations
        }
    )


# =========================
# API ДЛЯ ГРАФИКОВ
# =========================
def analytics_data(request):
    days = list(StudyDay.objects.all().order_by('date'))

    data = {
        'dates': [d.date.strftime('%Y-%m-%d') for d in days],
        'mood': [d.mood for d in days],
        'fatigue': [d.fatigue for d in days],
        'productivity': [d.productivity for d in days],
    }

    data['avg_productivity'] = (
        round(sum(data['productivity']) / len(data['productivity']), 2)
        if data['productivity'] else 0
    )

    return JsonResponse(data)
