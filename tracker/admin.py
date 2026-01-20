from django.contrib import admin
from .models import StudyDay, StudyMetric, Recommendation


@admin.register(StudyDay)
class StudyDayAdmin(admin.ModelAdmin):
    list_display = (
        'date',
        'mood',
        'fatigue',
        'productivity',
        'effectiveness_level',
        'created_at',
    )

    list_filter = (
        'date',
        'mood',
        'fatigue',
        'productivity',
    )

    search_fields = (
        'comment',
    )

    ordering = ('-date',)


@admin.register(StudyMetric)
class StudyMetricAdmin(admin.ModelAdmin):
    list_display = (
        'date',
        'avg_mood',
        'avg_fatigue',
        'avg_productivity',
    )

    ordering = ('-date',)


@admin.register(Recommendation)
class RecommendationAdmin(admin.ModelAdmin):
    list_display = (
        'study_day',
        'created_at',
    )

    search_fields = (
        'text',
    )

    ordering = ('-created_at',)