import requests
import datetime
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
from django.core.files.base import ContentFile
import seaborn as sns
import numpy as np


class HeadHunterAPI:
    """Класс для работы с API HeadHunter"""

    BASE_URL = 'https://api.hh.ru'

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'IT Profession Analyzer/1.0 (api@example.com)'
        })

    def search_vacancies(self, text, params=None, max_pages=10):
        """
        Поиск вакансий по заданным параметрам

        Args:
            text (str): Текст поискового запроса
            params (dict, optional): Дополнительные параметры запроса
            max_pages (int, optional): Максимальное количество страниц для загрузки

        Returns:
            list: Список вакансий
        """
        search_params = {
            'text': text,
            'per_page': 100,  # Максимальное количество вакансий на странице
        }

        if params:
            search_params.update(params)

        all_vacancies = []

        for page in range(max_pages):
            search_params['page'] = page
            response = self.session.get(f'{self.BASE_URL}/vacancies', params=search_params)

            if response.status_code != 200:
                break

            data = response.json()
            all_vacancies.extend(data.get('items', []))

            # Проверяем, есть ли еще страницы
            if page >= data.get('pages', 0) - 1:
                break

        return all_vacancies

    def get_vacancy_details(self, vacancy_id):
        """
        Получение детальной информации о вакансии

        Args:
            vacancy_id (str): Идентификатор вакансии

        Returns:
            dict: Детальная информация о вакансии
        """
        response = self.session.get(f'{self.BASE_URL}/vacancies/{vacancy_id}')

        if response.status_code == 200:
            return response.json()

        return None

    def get_salary_statistics(self, vacancies):
        """
        Получение статистики по зарплатам

        Args:
            vacancies (list): Список вакансий

        Returns:
            pandas.DataFrame: DataFrame с данными о зарплатах
        """
        salary_data = []

        for vacancy in vacancies:
            salary = vacancy.get('salary')
            if salary:
                # Преобразуем зарплату в рубли
                from_salary = salary.get('from')
                to_salary = salary.get('to')
                currency = salary.get('currency')

                # Конвертация в рубли
                avg_salary = self._calculate_average_salary(from_salary, to_salary, currency)

                if avg_salary:
                    published_at = datetime.datetime.strptime(
                        vacancy['published_at'], '%Y-%m-%dT%H:%M:%S%z'
                    )

                    salary_data.append({
                        'id': vacancy['id'],
                        'name': vacancy['name'],
                        'salary_avg_rub': avg_salary,
                        'area_name': vacancy['area']['name'],
                        'published_at': published_at,
                        'year': published_at.year,
                        'month': published_at.month
                    })

        return pd.DataFrame(salary_data)

    def get_skills_statistics(self, vacancies):
        """
        Получение статистики по навыкам

        Args:
            vacancies (list): Список вакансий

        Returns:
            pandas.DataFrame: DataFrame с данными о навыках
        """
        skills_data = []

        for vacancy in vacancies:
            vacancy_id = vacancy['id']
            details = self.get_vacancy_details(vacancy_id)

            if details and 'key_skills' in details:
                published_at = datetime.datetime.strptime(
                    vacancy['published_at'], '%Y-%m-%dT%H:%M:%S%z'
                )

                for skill in details['key_skills']:
                    skills_data.append({
                        'vacancy_id': vacancy_id,
                        'skill_name': skill['name'],
                        'year': published_at.year
                    })

        return pd.DataFrame(skills_data)

    def get_geography_statistics(self, vacancies):
        """
        Получение статистики по географии вакансий

        Args:
            vacancies (list): Список вакансий

        Returns:
            pandas.DataFrame: DataFrame с данными о географии вакансий
        """
        geography_data = []

        for vacancy in vacancies:
            area_name = vacancy['area']['name']
            salary = vacancy.get('salary')

            if salary:
                from_salary = salary.get('from')
                to_salary = salary.get('to')
                currency = salary.get('currency')

                avg_salary = self._calculate_average_salary(from_salary, to_salary, currency)
            else:
                avg_salary = None

            geography_data.append({
                'id': vacancy['id'],
                'area_name': area_name,
                'salary_avg_rub': avg_salary
            })

        return pd.DataFrame(geography_data)

    def _calculate_average_salary(self, from_salary, to_salary, currency):
        """
        Расчет средней зарплаты в рублях

        Args:
            from_salary (int): Нижняя граница зарплаты
            to_salary (int): Верхняя граница зарплаты
            currency (str): Валюта

        Returns:
            float: Средняя зарплата в рублях
        """
        # Курсы валют (примерные)
        currency_rates = {
            'RUR': 1.0,
            'USD': 75.0,
            'EUR': 85.0,
            'KZT': 0.17,
            'UAH': 2.7,
            'BYR': 30.0,
        }

        rate = currency_rates.get(currency, 1.0)

        if from_salary and to_salary:
            avg_salary = (from_salary + to_salary) / 2
        elif from_salary:
            avg_salary = from_salary
        elif to_salary:
            avg_salary = to_salary
        else:
            return None

        return avg_salary * rate

