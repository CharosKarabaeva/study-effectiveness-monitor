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
        'study_day',
        'metric_type',
        'value',
    )

    list_filter = (
        'metric_type',
    )

    search_fields = (
        'study_day__comment',
    )


@admin.register(Recommendation)
class RecommendationAdmin(admin.ModelAdmin):
    list_display = (
        'recommendation_type',
        'created_at',
    )

    list_filter = (
        'recommendation_type',
    )

    search_fields = (
        'text',
    )

    ordering = ('-created_at',)