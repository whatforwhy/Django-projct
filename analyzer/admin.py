from django.contrib import admin
from .models import (
    Profession, ProfessionImage, SalaryByYear, VacanciesByYear,
    SalaryByCity, VacanciesByCity, SkillsByYear
)

class ProfessionImageInline(admin.TabularInline):
    model = ProfessionImage
    extra = 1

@admin.register(Profession)
class ProfessionAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    inlines = [ProfessionImageInline]

@admin.register(SalaryByYear)
class SalaryByYearAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'is_general')
    list_filter = ('is_general', 'profession')

@admin.register(VacanciesByYear)
class VacanciesByYearAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'is_general')
    list_filter = ('is_general', 'profession')

@admin.register(SalaryByCity)
class SalaryByCityAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'is_general')
    list_filter = ('is_general', 'profession')

@admin.register(VacanciesByCity)
class VacanciesByCityAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'is_general')
    list_filter = ('is_general', 'profession')

@admin.register(SkillsByYear)
class SkillsByYearAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'year', 'is_general')
    list_filter = ('is_general', 'profession', 'year')
