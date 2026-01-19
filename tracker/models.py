from django.db import models


class StudyDay(models.Model):
    date = models.DateField(verbose_name='Дата')

    mood = models.IntegerField(
        verbose_name='Настроение',
        choices=[(i, i) for i in range(1, 6)]
    )

    fatigue = models.IntegerField(
        verbose_name='Усталость',
        choices=[(i, i) for i in range(1, 6)]
    )

    productivity = models.IntegerField(
        verbose_name='Продуктивность',
        choices=[(i, i) for i in range(1, 6)]
    )

    comment = models.TextField(
        verbose_name='Комментарий',
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f'{self.date} — продуктивность {self.productivity}'

    class Meta:
        verbose_name = 'День учёбы'
        verbose_name_plural = 'Дни учёбы'
        ordering = ['-date']

    @property
    def effectiveness_level(self):
        if self.productivity <= 2:
            return 'low'
        elif self.productivity == 3:
            return 'medium'
        return 'high'

class Recommendation(models.Model):
    study_day = models.ForeignKey(
        StudyDay,
        on_delete=models.CASCADE,
        related_name='recommendations',
        verbose_name='Учебный день'
    )
    text = models.TextField(
        verbose_name='Текст рекомендации'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )

    def __str__(self):
        return f"Рекомендация для {self.study_day.date}"

    class Meta:
        verbose_name = 'Рекомендация'
        verbose_name_plural = 'Рекомендации'

class StudyMetric(models.Model):
    date = models.DateField(
        verbose_name='Дата'
    )
    avg_mood = models.FloatField(
        verbose_name='Среднее настроение'
    )
    avg_fatigue = models.FloatField(
        verbose_name='Средняя усталость'
    )
    avg_productivity = models.FloatField(
        verbose_name='Средняя продуктивность'
    )

    def __str__(self):
        return f"Метрики за {self.date}"

    class Meta:
        verbose_name = 'Метрика учебной активности'
        verbose_name_plural = 'Метрики учебной активности'
