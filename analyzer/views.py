from django.shortcuts import render
from .models import (
    Profession, ProfessionImage, SalaryByYear, VacanciesByYear,
    SalaryByCity, VacanciesByCity, SkillsByYear
)
from .hh_api import HeadHunterAPI
import requests
import datetime
from django.core.files.base import ContentFile
import pandas as pd
from django.utils import timezone


def get_profession():
    # Получаем профессию UI/UX дизайнер из базы данных
    # Если профессии нет, создаем ее
    profession, created = Profession.objects.get_or_create(
        name="UI/UX дизайнер",
        defaults={
            'description': "UI/UX дизайнер — это специалист, который проектирует пользовательские интерфейсы и создает удобные, интуитивно понятные продукты. Он отвечает за то, чтобы взаимодействие пользователя с продуктом было максимально комфортным и эффективным.",
            'keywords': "UI/UX, UX/UI, UI дизайнер, UX дизайнер, дизайнер интерфейсов, проектировщик интерфейсов"
        }
    )
    return profession


def update_general_statistics():
    """Обновление общей статистики из API HeadHunter"""
    profession = get_profession()
    api = HeadHunterAPI()

    # Поиск вакансий UI/UX дизайнера
    search_text = "UI/UX дизайнер"
    vacancies = api.search_vacancies(search_text, max_pages=10)

    if not vacancies:
        return

    # Получение статистики по зарплатам
    salary_df = api.get_salary_statistics(vacancies)

    # Динамика уровня зарплат по годам
    salary_chart_buffer, salary_by_year_df = api.generate_salary_by_year_chart(
        salary_df,
        title="Динамика уровня зарплат по годам (UI/UX дизайнер)"
    )
    salary_by_year_html = api.generate_html_table(salary_by_year_df)

    # Сохраняем или обновляем данные в базе
    salary_by_year, created = SalaryByYear.objects.get_or_create(
        profession=profession,
        is_general=True,
        defaults={
            'content': salary_by_year_html,
            'data_source': 'HeadHunter API'
        }
    )

    if not created:
        salary_by_year.content = salary_by_year_html
        salary_by_year.data_source = 'HeadHunter API'
        salary_by_year.last_updated = timezone.now()

    salary_by_year.chart_image.save(
        f'salary_by_year_general_{timezone.now().strftime("%Y%m%d%H%M%S")}.png',
        ContentFile(salary_chart_buffer.getvalue())
    )

    # Динамика количества вакансий по годам
    vacancies_chart_buffer, vacancies_by_year_df = api.generate_vacancies_by_year_chart(
        salary_df,
        title="Динамика количества вакансий по годам (UI/UX дизайнер)"
    )
    vacancies_by_year_html = api.generate_html_table(vacancies_by_year_df)

    vacancies_by_year, created = VacanciesByYear.objects.get_or_create(
        profession=profession,
        is_general=True,
        defaults={
            'content': vacancies_by_year_html,
            'data_source': 'HeadHunter API'
        }
    )

    if not created:
        vacancies_by_year.content = vacancies_by_year_html
        vacancies_by_year.data_source = 'HeadHunter API'
        vacancies_by_year.last_updated = timezone.now()

    vacancies_by_year.chart_image.save(
        f'vacancies_by_year_general_{timezone.now().strftime("%Y%m%d%H%M%S")}.png',
        ContentFile(vacancies_chart_buffer.getvalue())
    )

    # Получение статистики по географии
    geography_df = api.get_geography_statistics(vacancies)

    # Уровень зарплат по городам
    salary_by_city_buffer, salary_by_city_df = api.generate_salary_by_city_chart(
        geography_df,
        title="Уровень зарплат по городам (UI/UX дизайнер)"
    )
    salary_by_city_html = api.generate_html_table(salary_by_city_df)

    salary_by_city, created = SalaryByCity.objects.get_or_create(
        profession=profession,
        is_general=True,
        defaults={
            'content': salary_by_city_html,
            'data_source': 'HeadHunter API'
        }
    )

    if not created:
        salary_by_city.content = salary_by_city_html
        salary_by_city.data_source = 'HeadHunter API'
        salary_by_city.last_updated = timezone.now()

    salary_by_city.chart_image.save(
        f'salary_by_city_general_{timezone.now().strftime("%Y%m%d%H%M%S")}.png',
        ContentFile(salary_by_city_buffer.getvalue())
    )

    # Доля вакансий по городам
    vacancies_by_city_buffer, vacancies_by_city_df = api.generate_vacancies_by_city_chart(
        geography_df,
        title="Доля вакансий по городам (UI/UX дизайнер)"
    )
    vacancies_by_city_html = api.generate_html_table(vacancies_by_city_df)

    vacancies_by_city, created = VacanciesByCity.objects.get_or_create(
        profession=profession,
        is_general=True,
        defaults={
            'content': vacancies_by_city_html,
            'data_source': 'HeadHunter API'
        }
    )

    if not created:
        vacancies_by_city.content = vacancies_by_city_html
        vacancies_by_city.data_source = 'HeadHunter API'
        vacancies_by_city.last_updated = timezone.now()

    vacancies_by_city.chart_image.save(
        f'vacancies_by_city_general_{timezone.now().strftime("%Y%m%d%H%M%S")}.png',
        ContentFile(vacancies_by_city_buffer.getvalue())
    )

    # Получение статистики по навыкам
    # Ограничиваем количество вакансий для получения навыков, чтобы не перегружать API
    skills_vacancies = vacancies[:50]  # Берем только первые 50 вакансий
    skills_df = api.get_skills_statistics(skills_vacancies)

    # Группируем навыки по годам
    years = skills_df['year'].unique()

    for year in years:
        year_skills_df = skills_df[skills_df['year'] == year]

        if len(year_skills_df) > 0:
            skills_chart_buffer, top_skills_df = api.generate_skills_chart(
                year_skills_df,
                year=year,
                title="ТОП-20 навыков (UI/UX дизайнер)"
            )
            skills_html = api.generate_html_table(top_skills_df)

            skills_by_year, created = SkillsByYear.objects.get_or_create(
                profession=profession,
                is_general=True,
                year=year,
                defaults={
                    'content': skills_html,
                    'data_source': 'HeadHunter API'
                }
            )

            if not created:
                skills_by_year.content = skills_html
                skills_by_year.data_source = 'HeadHunter API'
                skills_by_year.last_updated = timezone.now()

            skills_by_year.chart_image.save(
                f'skills_{year}_general_{timezone.now().strftime("%Y%m%d%H%M%S")}.png',
                ContentFile(skills_chart_buffer.getvalue())
            )


def update_profession_statistics():
    """Обновление статистики профессии из API HeadHunter"""
    profession = get_profession()
    api = HeadHunterAPI()

    # Поиск вакансий UI/UX дизайнера
    search_text = "UI/UX дизайнер"
    vacancies = api.search_vacancies(search_text)

    if not vacancies:
        return

    # Получение статистики по зарплатам
    salary_df = api.get_salary_statistics(vacancies)

    # Динамика уровня зарплат по годам
    salary_chart_buffer, salary_by_year_df = api.generate_salary_by_year_chart(
        salary_df,
        title=f"Динамика уровня зарплат по годам ({profession.name})"
    )
    salary_by_year_html = api.generate_html_table(salary_by_year_df)

    # Сохраняем или обновляем данные в базе
    salary_by_year, created = SalaryByYear.objects.get_or_create(
        profession=profession,
        is_general=False,
        defaults={
            'content': salary_by_year_html,
            'data_source': 'HeadHunter API'
        }
    )

    if not created:
        salary_by_year.content = salary_by_year_html
        salary_by_year.data_source = 'HeadHunter API'
        salary_by_year.last_updated = timezone.now()

    salary_by_year.chart_image.save(
        f'salary_by_year_{profession.name}_{timezone.now().strftime("%Y%m%d%H%M%S")}.png',
        ContentFile(salary_chart_buffer.getvalue())
    )

    # Динамика количества вакансий по годам
    vacancies_chart_buffer, vacancies_by_year_df = api.generate_vacancies_by_year_chart(
        salary_df,
        title=f"Динамика количества вакансий по годам ({profession.name})"
    )
    vacancies_by_year_html = api.generate_html_table(vacancies_by_year_df)

    vacancies_by_year, created = VacanciesByYear.objects.get_or_create(
        profession=profession,
        is_general=False,
        defaults={
            'content': vacancies_by_year_html,
            'data_source': 'HeadHunter API'
        }
    )

    if not created:
        vacancies_by_year.content = vacancies_by_year_html
        vacancies_by_year.data_source = 'HeadHunter API'
        vacancies_by_year.last_updated = timezone.now()

    vacancies_by_year.chart_image.save(
        f'vacancies_by_year_{profession.name}_{timezone.now().strftime("%Y%m%d%H%M%S")}.png',
        ContentFile(vacancies_chart_buffer.getvalue())
    )

    # Получение статистики по географии
    geography_df = api.get_geography_statistics(vacancies)

    # Уровень зарплат по городам
    salary_by_city_buffer, salary_by_city_df = api.generate_salary_by_city_chart(
        geography_df,
        title=f"Уровень зарплат по городам ({profession.name})"
    )
    salary_by_city_html = api.generate_html_table(salary_by_city_df)

    salary_by_city, created = SalaryByCity.objects.get_or_create(
        profession=profession,
        is_general=False,
        defaults={
            'content': salary_by_city_html,
            'data_source': 'HeadHunter API'
        }
    )

    if not created:
        salary_by_city.content = salary_by_city_html
        salary_by_city.data_source = 'HeadHunter API'
        salary_by_city.last_updated = timezone.now()

    salary_by_city.chart_image.save(
        f'salary_by_city_{profession.name}_{timezone.now().strftime("%Y%m%d%H%M%S")}.png',
        ContentFile(salary_by_city_buffer.getvalue())
    )

    # Доля вакансий по городам
    vacancies_by_city_buffer, vacancies_by_city_df = api.generate_vacancies_by_city_chart(
        geography_df,
        title=f"Доля вакансий по городам ({profession.name})"
    )
    vacancies_by_city_html = api.generate_html_table(vacancies_by_city_df)

    vacancies_by_city, created = VacanciesByCity.objects.get_or_create(
        profession=profession,
        is_general=False,
        defaults={
            'content': vacancies_by_city_html,
            'data_source': 'HeadHunter API'
        }
    )

    if not created:
        vacancies_by_city.content = vacancies_by_city_html
        vacancies_by_city.data_source = 'HeadHunter API'
        vacancies_by_city.last_updated = timezone.now()

    vacancies_by_city.chart_image.save(
        f'vacancies_by_city_{profession.name}_{timezone.now().strftime("%Y%m%d%H%M%S")}.png',
        ContentFile(vacancies_by_city_buffer.getvalue())
    )

    # Получение статистики по навыкам
    # Ограничиваем количество вакансий для получения навыков, чтобы не перегружать API
    skills_vacancies = vacancies[:100]  # Берем только первые 100 вакансий
    skills_df = api.get_skills_statistics(skills_vacancies)

    # Группируем навыки по годам
    years = skills_df['year'].unique()

    for year in years:
        year_skills_df = skills_df[skills_df['year'] == year]

        if len(year_skills_df) > 0:
            skills_chart_buffer, top_skills_df = api.generate_skills_chart(
                year_skills_df,
                year=year,
                title=f"ТОП-20 навыков ({profession.name})"
            )
            skills_html = api.generate_html_table(top_skills_df)

            skills_by_year, created = SkillsByYear.objects.get_or_create(
                profession=profession,
                is_general=False,
                year=year,
                defaults={
                    'content': skills_html,
                    'data_source': 'HeadHunter API'
                }
            )

            if not created:
                skills_by_year.content = skills_html
                skills_by_year.data_source = 'HeadHunter API'
                skills_by_year.last_updated = timezone.now()

            skills_by_year.chart_image.save(
                f'skills_{year}_{profession.name}_{timezone.now().strftime("%Y%m%d%H%M%S")}.png',
                ContentFile(skills_chart_buffer.getvalue())
            )


def home(request):
    profession = get_profession()
    if not profession:
        return render(request, 'analyzer/no_profession.html')

    images = profession.images.all()

    context = {
        'profession': profession,
        'images': images,
    }
    return render(request, 'analyzer/home.html', context)


def general_statistics(request):
    profession = get_profession()
    if not profession:
        return render(request, 'analyzer/no_profession.html')

    # Проверяем, есть ли данные в базе
    salary_by_year = SalaryByYear.objects.filter(is_general=True).first()

    # Если данных нет или они устарели (старше 24 часов), обновляем их
    if not salary_by_year or (timezone.now() - salary_by_year.last_updated).days >= 1:
        update_general_statistics()

    # Получаем обновленные данные
    salary_by_year = SalaryByYear.objects.filter(is_general=True).first()
    vacancies_by_year = VacanciesByYear.objects.filter(is_general=True).first()
    salary_by_city = SalaryByCity.objects.filter(is_general=True).first()
    vacancies_by_city = VacanciesByCity.objects.filter(is_general=True).first()

    # Получаем все навыки по годам для общей статистики
    skills_by_year = SkillsByYear.objects.filter(is_general=True).order_by('-year')[:10]  # Ограничиваем до 10 записей

    context = {
        'profession': profession,
        'salary_by_year': salary_by_year,
        'vacancies_by_year': vacancies_by_year,
        'salary_by_city': salary_by_city,
        'vacancies_by_city': vacancies_by_city,
        'skills_by_year': skills_by_year,
    }
    return render(request, 'analyzer/general_statistics.html', context)


def demand(request):
    profession = get_profession()
    if not profession:
        return render(request, 'analyzer/no_profession.html')

    # Проверяем, есть ли данные в базе
    salary_by_year = SalaryByYear.objects.filter(profession=profession, is_general=False).first()

    # Если данных нет или они устарели (старше 24 часов), обновляем их
    if not salary_by_year or (timezone.now() - salary_by_year.last_updated).days >= 1:
        update_profession_statistics()

    # Получаем обновленные данные
    salary_by_year = SalaryByYear.objects.filter(profession=profession, is_general=False).first()
    vacancies_by_year = VacanciesByYear.objects.filter(profession=profession, is_general=False).first()

    context = {
        'profession': profession,
        'salary_by_year': salary_by_year,
        'vacancies_by_year': vacancies_by_year,
    }
    return render(request, 'analyzer/demand.html', context)


def geography(request):
    profession = get_profession()
    if not profession:
        return render(request, 'analyzer/no_profession.html')

    # Проверяем, есть ли данные в базе
    salary_by_city = SalaryByCity.objects.filter(profession=profession, is_general=False).first()

    # Если данных нет или они устарели (старше 24 часов), обновляем их
    if not salary_by_city or (timezone.now() - salary_by_city.last_updated).days >= 1:
        update_profession_statistics()

    # Получаем обновленные данные
    salary_by_city = SalaryByCity.objects.filter(profession=profession, is_general=False).first()
    vacancies_by_city = VacanciesByCity.objects.filter(profession=profession, is_general=False).first()

    context = {
        'profession': profession,
        'salary_by_city': salary_by_city,
        'vacancies_by_city': vacancies_by_city,
    }
    return render(request, 'analyzer/geography.html', context)


def skills(request):
    profession = get_profession()
    if not profession:
        return render(request, 'analyzer/no_profession.html')

    # Проверяем, есть ли данные в базе
    skills_by_year = SkillsByYear.objects.filter(profession=profession, is_general=False).first()

    # Если данных нет или они устарели (старше 24 часов), обновляем их
    if not skills_by_year or (timezone.now() - skills_by_year.last_updated).days >= 1:
        update_profession_statistics()

    # Получаем обновленные данные
    skills_by_year = SkillsByYear.objects.filter(profession=profession, is_general=False).order_by('-year')

    context = {
        'profession': profession,
        'skills_by_year': skills_by_year,
    }
    return render(request, 'analyzer/skills.html', context)


def latest_vacancies(request):
    profession = get_profession()
    if not profession:
        return render(request, 'analyzer/no_profession.html')

    # Получаем ключевые слова для поиска
    keywords = [kw.strip() for kw in profession.keywords.split(',')]

    # Формируем поисковый запрос (первое ключевое слово)
    search_query = "UI/UX дизайнер"

    # Получаем вакансии через API HH
    vacancies = get_hh_vacancies(search_query)

    context = {
        'profession': profession,
        'vacancies': vacancies,
    }
    return render(request, 'analyzer/latest_vacancies.html', context)


def get_hh_vacancies(search_query):
    # Получение текущей даты и даты сутки назад
    today = datetime.datetime.now()
    yesterday = today - datetime.timedelta(days=1)
    date_from = yesterday.strftime("%Y-%m-%dT%H:%M:%S")

    # Параметры запроса к API HH
    params = {
        'text': search_query,
        'specialization': 1,  # ИТ
        'date_from': date_from,
        'per_page': 10,
        'order_by': 'publication_time'
    }

    try:
        response = requests.get('https://api.hh.ru/vacancies', params=params)
        data = response.json()

        vacancies = []
        for item in data.get('items', []):
            # Получение детальной информации о вакансии
            vacancy_details = get_vacancy_details(item['id'])

            # Формирование данных о вакансии
            vacancy = {
                'id': item['id'],
                'name': item['name'],
                'company': item['employer']['name'],
                'area': item['area']['name'],
                'published_at': item['published_at'],
                'salary': format_salary(item.get('salary')),
                'description': vacancy_details.get('description', ''),
                'skills': ', '.join([skill['name'] for skill in vacancy_details.get('key_skills', [])])
            }
            vacancies.append(vacancy)

        return vacancies
    except Exception as e:
        print(f"Error fetching vacancies: {e}")
        return []


def get_vacancy_details(vacancy_id):
    try:
        response = requests.get(f'https://api.hh.ru/vacancies/{vacancy_id}')
        return response.json()
    except Exception as e:
        print(f"Error fetching vacancy details: {e}")
        return {}


def format_salary(salary_data):
    if not salary_data:
        return "Не указана"

    from_salary = salary_data.get('from')
    to_salary = salary_data.get('to')
    currency = salary_data.get('currency', '')

    if from_salary and to_salary:
        return f"{from_salary} - {to_salary} {currency}"
    elif from_salary:
        return f"от {from_salary} {currency}"
    elif to_salary:
        return f"до {to_salary} {currency}"
    else:
        return "Не указана"
