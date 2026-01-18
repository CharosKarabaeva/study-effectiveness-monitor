from django.contrib import admin
from .models import StudyDay


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
