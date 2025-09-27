#!/usr/bin/env python3
"""
Веб-сервер для отображения и обновления данных о вакансиях
"""

import os
import json
import threading
import time
from flask import Flask, render_template_string, jsonify, request, send_from_directory
from hirehi_scraper import HireHiScraper

app = Flask(__name__)

# Глобальные переменные для хранения данных
current_jobs = []
total_jobs_count = 0
is_refreshing = False

def load_existing_data():
    """Загружает существующие данные из JSON файла"""
    global current_jobs, total_jobs_count
    
    try:
        if os.path.exists('hirehi_filtered_jobs.json'):
            with open('hirehi_filtered_jobs.json', 'r', encoding='utf-8') as f:
                current_jobs = json.load(f)
            print(f"Загружено {len(current_jobs)} вакансий из файла")
    except Exception as e:
        print(f"Ошибка загрузки данных: {e}")
        current_jobs = []

def run_scraper():
    """Запускает скрапинг в отдельном потоке"""
    global current_jobs, total_jobs_count, is_refreshing
    
    is_refreshing = True
    print("Начинаем обновление данных...")
    
    try:
        scraper = HireHiScraper()
        keywords = ["Kotlin", "Android"]
        
        # Получаем все вакансии
        all_jobs = scraper.get_all_jobs()
        
        if not all_jobs:
            print("Не удалось получить вакансии")
            return
        
        print(f"Получено {len(all_jobs)} вакансий до фильтрации")
        total_jobs_count = len(all_jobs)
        
        # Фильтруем по ключевым словам
        filtered_jobs = scraper.filter_jobs_by_keywords(all_jobs, keywords)
        print(f"После фильтрации: {len(filtered_jobs)} вакансий")
        
        if filtered_jobs:
            # Сохраняем в JSON файл
            scraper.save_to_json(filtered_jobs, "hirehi_filtered_jobs.json")
            
            # Обновляем глобальные данные
            current_jobs = filtered_jobs
            
            print("Данные успешно обновлены!")
        else:
            print("После фильтрации не осталось вакансий")
            
    except Exception as e:
        print(f"Ошибка при обновлении данных: {e}")
    finally:
        is_refreshing = False

@app.route('/')
def index():
    """Главная страница"""
    global current_jobs, total_jobs_count
    
    # Загружаем HTML шаблон
    with open('jobs_template.html', 'r', encoding='utf-8') as f:
        html_template = f.read()
    
    # Подготавливаем данные для JavaScript
    jobs_data = []
    scraper = HireHiScraper()
    for job in current_jobs:
        job_info = scraper.extract_job_info(job)
        jobs_data.append(job_info)
    
    # Создаем JavaScript код для вставки данных
    js_data = f"""
    <script>
        // Данные вакансий
        const jobsData = {json.dumps(jobs_data, ensure_ascii=False, indent=2)};
        const totalJobsCount = {total_jobs_count};
    </script>
    """
    
    # Вставляем JavaScript перед закрывающим тегом body
    html_content = html_template.replace('</body>', f'{js_data}\n</body>')
    
    return html_content

@app.route('/api/refresh', methods=['POST'])
def refresh_data():
    """API endpoint для обновления данных"""
    global is_refreshing
    
    if is_refreshing:
        return jsonify({
            'success': False,
            'error': 'Обновление уже выполняется'
        }), 409
    
    # Запускаем скрапинг в отдельном потоке
    thread = threading.Thread(target=run_scraper)
    thread.daemon = True
    thread.start()
    
    # Ждем завершения обновления (максимум 60 секунд)
    timeout = 60
    start_time = time.time()
    
    while is_refreshing and (time.time() - start_time) < timeout:
        time.sleep(1)
    
    if is_refreshing:
        return jsonify({
            'success': False,
            'error': 'Таймаут обновления данных'
        }), 408
    
    # Возвращаем обновленные данные
    scraper = HireHiScraper()
    jobs_data = []
    for job in current_jobs:
        job_info = scraper.extract_job_info(job)
        jobs_data.append(job_info)
    
    return jsonify({
        'success': True,
        'jobs': jobs_data,
        'total_count': total_jobs_count,
        'filtered_count': len(jobs_data)
    })

@app.route('/api/status')
def get_status():
    """API endpoint для получения статуса"""
    return jsonify({
        'is_refreshing': is_refreshing,
        'jobs_count': len(current_jobs),
        'total_count': total_jobs_count
    })

if __name__ == '__main__':
    # Загружаем существующие данные при запуске
    load_existing_data()
    
    print("Запуск веб-сервера...")
    print("Откройте браузер и перейдите по адресу: http://localhost:5000")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
