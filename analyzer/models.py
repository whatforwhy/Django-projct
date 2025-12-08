from django.db import models


class Profession(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название профессии")
    description = models.TextField(verbose_name="Описание профессии")
    keywords = models.TextField(verbose_name="Ключевые слова для поиска",
                                help_text="Введите ключевые слова через запятую")
    last_updated = models.DateTimeField(auto_now=True, verbose_name="Последнее обновление")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Профессия"
        verbose_name_plural = "Профессии"


class ProfessionImage(models.Model):
    profession = models.ForeignKey(Profession, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='profession_images/', verbose_name="Изображение")

    def __str__(self):
        return f"Изображение для {self.profession.name}"

    class Meta:
        verbose_name = "Изображение профессии"
        verbose_name_plural = "Изображения профессий"


class SalaryByYear(models.Model):
    profession = models.ForeignKey(Profession, on_delete=models.CASCADE, related_name='salary_by_year', null=True,
                                   blank=True)
    is_general = models.BooleanField(default=False, verbose_name="Общая статистика")
    content = models.TextField(verbose_name="HTML-содержимое таблицы")
    chart_image = models.ImageField(upload_to='charts/', verbose_name="Изображение графика")
    data_source = models.CharField(max_length=50, default="CSV", verbose_name="Источник данных")
    last_updated = models.DateTimeField(auto_now=True, verbose_name="Последнее обновление")

    def __str__(self):
        if self.is_general:
            return "Динамика уровня зарплат по годам (общая)"
        return f"Динамика уровня зарплат по годам ({self.profession.name})"

    class Meta:
        verbose_name = "Статистика зарплат по годам"
        verbose_name_plural = "Статистика зарплат по годам"


class VacanciesByYear(models.Model):
    profession = models.ForeignKey(Profession, on_delete=models.CASCADE, related_name='vacancies_by_year', null=True,
                                   blank=True)
    is_general = models.BooleanField(default=False, verbose_name="Общая статистика")
    content = models.TextField(verbose_name="HTML-содержимое таблицы")
    chart_image = models.ImageField(upload_to='charts/', verbose_name="Изображение графика")
    data_source = models.CharField(max_length=50, default="CSV", verbose_name="Источник данных")
    last_updated = models.DateTimeField(auto_now=True, verbose_name="Последнее обновление")

    def __str__(self):
        if self.is_general:
            return "Динамика количества вакансий по годам (общая)"
        return f"Динамика количества вакансий по годам ({self.profession.name})"

    class Meta:
        verbose_name = "Статистика вакансий по годам"
        verbose_name_plural = "Статистика вакансий по годам"


class SalaryByCity(models.Model):
    profession = models.ForeignKey(Profession, on_delete=models.CASCADE, related_name='salary_by_city', null=True,
                                   blank=True)
    is_general = models.BooleanField(default=False, verbose_name="Общая статистика")
    content = models.TextField(verbose_name="HTML-содержимое таблицы")
    chart_image = models.ImageField(upload_to='charts/', verbose_name="Изображение графика")
    data_source = models.CharField(max_length=50, default="CSV", verbose_name="Источник данных")
    last_updated = models.DateTimeField(auto_now=True, verbose_name="Последнее обновление")

    def __str__(self):
        if self.is_general:
            return "Уровень зарплат по городам (общая)"
        return f"Уровень зарплат по городам ({self.profession.name})"

    class Meta:
        verbose_name = "Статистика зарплат по городам"
        verbose_name_plural = "Статистика зарплат по городам"


class VacanciesByCity(models.Model):
    profession = models.ForeignKey(Profession, on_delete=models.CASCADE, related_name='vacancies_by_city', null=True,
                                   blank=True)
    is_general = models.BooleanField(default=False, verbose_name="Общая статистика")
    content = models.TextField(verbose_name="HTML-содержимое таблицы")
    chart_image = models.ImageField(upload_to='charts/', verbose_name="Изображение графика")
    data_source = models.CharField(max_length=50, default="CSV", verbose_name="Источник данных")
    last_updated = models.DateTimeField(auto_now=True, verbose_name="Последнее обновление")

    def __str__(self):
        if self.is_general:
            return "Доля вакансий по городам (общая)"
        return f"Доля вакансий по городам ({self.profession.name})"

    class Meta:
        verbose_name = "Статистика доли вакансий по городам"
        verbose_name_plural = "Статистика доли вакансий по городам"


class SkillsByYear(models.Model):
    profession = models.ForeignKey(Profession, on_delete=models.CASCADE, related_name='skills_by_year', null=True,
                                   blank=True)
    is_general = models.BooleanField(default=False, verbose_name="Общая статистика")
    year = models.IntegerField(verbose_name="Год")
    content = models.TextField(verbose_name="HTML-содержимое таблицы")
    chart_image = models.ImageField(upload_to='charts/', verbose_name="Изображение графика")
    data_source = models.CharField(max_length=50, default="CSV", verbose_name="Источник данных")
    last_updated = models.DateTimeField(auto_now=True, verbose_name="Последнее обновление")

    def __str__(self):
        if self.is_general:
            return f"ТОП-20 навыков за {self.year} год (общая)"
        return f"ТОП-20 навыков за {self.year} год ({self.profession.name})"

    class Meta:
        verbose_name = "Статистика навыков по годам"
        verbose_name_plural = "Статистика навыков по годам"
