from django import forms
from .models import StudyDay


class StudyDayForm(forms.ModelForm):
    class Meta:
        model = StudyDay
        fields = ['date', 'mood', 'fatigue', 'productivity', 'comment']

        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'comment': forms.Textarea(attrs={'rows': 2}),
        }
