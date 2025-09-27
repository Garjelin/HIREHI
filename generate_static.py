#!/usr/bin/env python3
"""
Скрипт для генерации статической версии сайта для GitHub Pages
"""

import json
import os
from hirehi_scraper import HireHiScraper

def generate_static_site():
    """Генерирует статическую версию сайта с актуальными данными"""
    
    print("Генерация статической версии сайта...")
    
    # Загружаем существующие данные
    jobs_data = []
    total_count = 0
    
    try:
        if os.path.exists('hirehi_filtered_jobs.json'):
            with open('hirehi_filtered_jobs.json', 'r', encoding='utf-8') as f:
                jobs_data = json.load(f)
            print(f"Загружено {len(jobs_data)} вакансий из файла")
    except Exception as e:
        print(f"Ошибка загрузки данных: {e}")
    
    # Читаем HTML шаблон
    with open('index.html', 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Подготавливаем данные для JavaScript
    scraper = HireHiScraper()
    processed_jobs = []
    for job in jobs_data:
        job_info = scraper.extract_job_info(job)
        processed_jobs.append(job_info)
    
    # Создаем JavaScript код для вставки данных
    js_data = f"""
    <script>
        // Данные вакансий
        const jobsData = {json.dumps(processed_jobs, ensure_ascii=False, indent=2)};
        const totalJobsCount = {len(jobs_data)};
    </script>
    """
    
    # Вставляем JavaScript перед закрывающим тегом body
    html_content = html_content.replace('</body>', f'{js_data}\n</body>')
    
    # Сохраняем готовую страницу
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"Статическая версия создана: index.html")
    print(f"Обработано {len(processed_jobs)} вакансий")
    
    return len(processed_jobs)

if __name__ == "__main__":
    generate_static_site()
