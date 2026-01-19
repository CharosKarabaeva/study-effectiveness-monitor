from django.contrib import admin
from .models import StudyDay, Recommendation, StudyMetric


@admin.register(StudyDay)
class StudyDayAdmin(admin.ModelAdmin):
    list_display = (
        'date',
        'mood',
        'fatigue',
        'productivity',
        'created_at',
    )
    list_filter = ('date', 'productivity', 'mood')
    search_fields = ('comment',)


@admin.register(Recommendation)
class RecommendationAdmin(admin.ModelAdmin):
    list_display = ('study_day', 'created_at')
    search_fields = ('text',)


@admin.register(StudyMetric)
class StudyMetricAdmin(admin.ModelAdmin):
    list_display = ('date', 'avg_mood', 'avg_fatigue', 'avg_productivity')