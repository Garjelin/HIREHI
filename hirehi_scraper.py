#!/usr/bin/env python3
"""
Скрипт для получения данных о вакансиях с сайта hirehi.ru
Получает информацию о QA вакансиях с удаленной работой (senior/middle, auto)
"""

import requests
import json
import logging
import time
from typing import List, Dict, Optional
from urllib.parse import urlencode

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('hirehi_scraper.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class HireHiScraper:
    """Класс для работы с API hirehi.ru"""
    
    def __init__(self):
        self.base_url = "https://hirehi.ru"
        self.api_url = f"{self.base_url}/api/search/jobs"
        self.session = requests.Session()
        
        # Настройка заголовков для имитации браузера
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'ru-RU,ru;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Referer': 'https://hirehi.ru/',
        })
        
        # Установка адаптера для автоматической декомпрессии
        from requests.adapters import HTTPAdapter
        from urllib3.util.retry import Retry
        
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
    
    def get_jobs_page(self, page: int = 1, limit: int = 27) -> Optional[Dict]:
        """
        Получает одну страницу вакансий
        
        Args:
            page: Номер страницы
            limit: Количество вакансий на странице
            
        Returns:
            Словарь с данными ответа или None в случае ошибки
        """
        params = {
            'page': page,
            'limit': limit,
            'sort': 'date',
            'category': 'qa',
            'format': 'удалённо',
            'level': ['senior', 'middle'],
            'subcategory': 'auto'
        }
        
        try:
            logger.info(f"Запрашиваем страницу {page} с лимитом {limit}")
            response = self.session.get(self.api_url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            jobs = data.get('jobs', [])
            logger.info(f"Получено {len(jobs)} вакансий на странице {page}")
            return data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка при запросе страницы {page}: {e}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"Ошибка парсинга JSON на странице {page}: {e}")
            return None
    
    def get_all_jobs(self) -> List[Dict]:
        """
        Получает все вакансии с учетом пагинации
        
        Returns:
            Список всех вакансий
        """
        all_jobs = []
        page = 1
        limit = 27
        
        while True:
            data = self.get_jobs_page(page, limit)
            
            if not data:
                logger.warning(f"Не удалось получить данные для страницы {page}")
                break
            
            jobs = data.get('jobs', [])
            if not jobs:
                logger.info(f"Страница {page} пуста, завершаем сбор данных")
                break
            
            all_jobs.extend(jobs)
            logger.info(f"Всего собрано вакансий: {len(all_jobs)}")
            
            # Проверяем, есть ли еще страницы
            has_more = data.get('has_more', False)
            if not has_more:
                logger.info(f"Достигнута последняя страница: {page}")
                break
            
            page += 1
            
            # Небольшая пауза между запросами
            time.sleep(1)
        
        return all_jobs
    
    def extract_job_info(self, job: Dict) -> Dict:
        """
        Извлекает нужную информацию из объекта вакансии
        
        Args:
            job: Объект вакансии
            
        Returns:
            Словарь с извлеченной информацией
        """
        # Компания может быть строкой или объектом
        company = job.get('company', 'Не указано')
        if isinstance(company, dict):
            company_name = company.get('name', 'Не указано')
        else:
            company_name = company
        
        return {
            'title': job.get('title', 'Не указано'),
            'company': company_name,
            'salary': job.get('salary', 'Не указано'),
            'level': job.get('level', 'Не указано'),
            'format': job.get('format', 'Не указано'),
            'url': f"{self.base_url}/job/{job.get('id', '')}" if job.get('id') else 'Не указано'
        }
    
    
    def log_jobs(self, jobs: List[Dict]):
        """
        Выводит информацию о вакансиях в лог
        
        Args:
            jobs: Список вакансий
        """
        logger.info("=" * 80)
        logger.info(f"НАЙДЕНО ВАКАНСИЙ: {len(jobs)}")
        logger.info("=" * 80)
        
        for i, job in enumerate(jobs, 1):
            job_info = self.extract_job_info(job)
            logger.info(f"{i:3d}. {job_info['company']} - {job_info['title']}")
            logger.info(f"     Зарплата: {job_info['salary']}")
            logger.info(f"     Уровень: {job_info['level']} | Формат: {job_info['format']}")
            logger.info(f"     Ссылка: {job_info['url']}")
            logger.info("-" * 60)
    
    def save_to_json(self, jobs: List[Dict], filename: str = "hirehi_jobs.json"):
        """
        Сохраняет данные в JSON файл
        
        Args:
            jobs: Список вакансий
            filename: Имя файла для сохранения
        """
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(jobs, f, ensure_ascii=False, indent=2)
            logger.info(f"Данные сохранены в файл: {filename}")
        except Exception as e:
            logger.error(f"Ошибка при сохранении в файл {filename}: {e}")


def main():
    """Основная функция"""
    logger.info("Запуск скрапера hirehi.ru")
    
    scraper = HireHiScraper()
    
    try:
        # Получаем все вакансии
        jobs = scraper.get_all_jobs()
        
        if not jobs:
            logger.warning("Не удалось получить ни одной вакансии")
            return
        
        # Выводим информацию в лог
        scraper.log_jobs(jobs)
        
        # Сохраняем в JSON файл
        scraper.save_to_json(jobs)
        
        logger.info("Скрапинг завершен успешно!")
        
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")


if __name__ == "__main__":
    main()
