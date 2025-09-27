#!/usr/bin/env python3
"""
Простой веб-сервер для отображения и обновления данных о вакансиях
Использует встроенные модули Python без внешних зависимостей
"""

import os
import json
import threading
import time
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
from hirehi_scraper import HireHiScraper

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

class WebHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Обработка GET запросов"""
        if self.path == '/' or self.path == '/index.html':
            self.serve_index()
        elif self.path == '/api/status':
            self.serve_status()
        else:
            self.send_error(404)
    
    def do_POST(self):
        """Обработка POST запросов"""
        if self.path == '/api/refresh':
            self.handle_refresh()
        else:
            self.send_error(404)
    
    def serve_index(self):
        """Отдает главную страницу"""
        global current_jobs, total_jobs_count
        
        try:
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
            
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(html_content.encode('utf-8'))
            
        except Exception as e:
            self.send_error(500, f"Ошибка загрузки страницы: {e}")
    
    def serve_status(self):
        """Отдает статус сервера"""
        global is_refreshing, current_jobs, total_jobs_count
        
        status = {
            'is_refreshing': is_refreshing,
            'jobs_count': len(current_jobs),
            'total_count': total_jobs_count
        }
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(status, ensure_ascii=False).encode('utf-8'))
    
    def handle_refresh(self):
        """Обрабатывает запрос на обновление данных"""
        global is_refreshing
        
        if is_refreshing:
            response = {
                'success': False,
                'error': 'Обновление уже выполняется'
            }
            self.send_response(409)
        else:
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
                response = {
                    'success': False,
                    'error': 'Таймаут обновления данных'
                }
                self.send_response(408)
            else:
                # Возвращаем обновленные данные
                scraper = HireHiScraper()
                jobs_data = []
                for job in current_jobs:
                    job_info = scraper.extract_job_info(job)
                    jobs_data.append(job_info)
                
                response = {
                    'success': True,
                    'jobs': jobs_data,
                    'total_count': total_jobs_count,
                    'filtered_count': len(jobs_data)
                }
                self.send_response(200)
        
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
    
    def log_message(self, format, *args):
        """Отключаем логирование запросов"""
        pass

def main():
    """Основная функция"""
    global current_jobs, total_jobs_count
    
    # Загружаем существующие данные при запуске
    load_existing_data()
    
    # Создаем сервер
    server_address = ('', 5000)
    httpd = HTTPServer(server_address, WebHandler)
    
    print("Запуск веб-сервера...")
    print("Откройте браузер и перейдите по адресу: http://localhost:5000")
    print("Для остановки сервера нажмите Ctrl+C")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nОстановка сервера...")
        httpd.shutdown()

if __name__ == '__main__':
    main()
