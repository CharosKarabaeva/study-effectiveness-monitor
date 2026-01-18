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

