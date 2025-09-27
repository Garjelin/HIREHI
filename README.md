# QA Вакансии - HireHi Scraper

Скрипт для автоматического сбора и отображения QA вакансий с сайта hirehi.ru с фильтрацией по ключевым словам Kotlin и Android.

## 🌐 Онлайн версии

**Статическая версия (GitHub Pages):** [https://garjelin.github.io/HIREHI/](https://garjelin.github.io/HIREHI/)

**Интерактивная версия (Render.com):** [https://hirehi-qa-jobs.onrender.com/](https://hirehi-qa-jobs.onrender.com/) *(с кнопкой обновления)*

## 🚀 Возможности

- **Автоматический сбор** вакансий с hirehi.ru
- **Фильтрация** по ключевым словам (Kotlin, Android)
- **Красивый веб-интерфейс** с современным дизайном
- **Кликабельные ссылки** на вакансии
- **Статическая версия** для GitHub Pages
- **Интерактивная версия** с кнопкой обновления на Render.com

## 📋 Требования

- Python 3.7+
- requests
- Flask (для Render.com версии)
- webbrowser (встроенный модуль)

## 🛠 Установка и запуск

### 1. Клонирование репозитория
```bash
git clone https://github.com/Garjelin/HIREHI.git
cd HIREHI
```

### 2. Установка зависимостей
```bash
# Для локального запуска
pip install requests

# Для Flask приложения (Render.com)
pip install -r requirements.txt
```

### 3. Запуск скрипта
```bash
# Простой запуск с открытием браузера
python hirehi_scraper.py

# Генерация статической версии для GitHub Pages
python generate_static.py

# Запуск Flask приложения (для Render.com)
python app.py
```

## 📁 Структура проекта

```
HIREHI/
├── hirehi_scraper.py      # Основной скрипт
├── jobs_template.html     # HTML шаблон
├── index.html            # Статическая версия для GitHub Pages
├── generate_static.py    # Генератор статической версии
├── app.py               # Flask приложение для Render.com
├── requirements.txt     # Зависимости для Flask
├── render.yaml         # Конфигурация для Render.com
├── .gitignore          # Исключения для Git
└── README.md
```

## 🔧 Настройка

### Изменение ключевых слов для фильтрации
В файле `hirehi_scraper.py` найдите строку:
```python
keywords = ["Kotlin", "Android"]
```
И измените на нужные вам ключевые слова.

### Изменение параметров поиска
В методе `get_jobs_page()` можно изменить:
- `category`: категория вакансий (по умолчанию 'qa')
- `format`: формат работы (по умолчанию 'удалённо')
- `level`: уровень (по умолчанию ['senior', 'middle'])
- `subcategory`: подкатегория (по умолчанию 'auto')

## 🌐 Развертывание

### GitHub Pages (Статическая версия)

#### Автоматическое обновление
1. Запустите скрипт локально для получения свежих данных
2. Выполните `python generate_static.py` для обновления статической версии
3. Зафиксируйте изменения и отправьте в репозиторий:
```bash
git add .
git commit -m "Обновление данных вакансий"
git push origin main
```

#### Настройка GitHub Pages
1. Перейдите в Settings вашего репозитория
2. Найдите раздел "Pages"
3. В "Source" выберите "Deploy from a branch"
4. Выберите ветку "main" и папку "/ (root)"
5. Сохраните настройки

### Render.com (Интерактивная версия)

#### Развертывание на Render.com
1. Зарегистрируйтесь на [render.com](https://render.com)
2. Подключите ваш GitHub репозиторий
3. Создайте новый Web Service:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python app.py`
   - **Environment:** Python 3
4. Render автоматически развернет ваше приложение

#### Преимущества Render.com версии:
- ✅ **Кнопка обновления** - обновляйте данные без перезапуска
- ✅ **API endpoints** - `/api/refresh` и `/api/status`
- ✅ **Автоматическое развертывание** из GitHub
- ✅ **Бесплатный тариф** для небольших проектов

## 📊 Формат данных

Скрипт сохраняет данные в JSON формате:
```json
{
  "title": "QA Engineer (auto)",
  "company": "Название компании",
  "salary": "от 200 000 ₽",
  "level": "senior",
  "format": "удалённо",
  "url": "https://hirehi.ru/qa/qa-testirovshchik-auto-1234"
}
```

## 🔄 Обновление данных

### GitHub Pages (Статическая версия)
1. Запустите `python hirehi_scraper.py` для сбора новых данных
2. Запустите `python generate_static.py` для генерации статической версии
3. Зафиксируйте изменения и отправьте в репозиторий

### Render.com (Интерактивная версия)
- **Автоматическое обновление** через кнопку "🔄 Обновить данные" на сайте
- **API endpoint** `/api/refresh` для программного обновления

## 📝 Логирование

Скрипт создает файл `hirehi_scraper.log` с подробной информацией о работе.

## 🤝 Вклад в проект

1. Форкните репозиторий
2. Создайте ветку для новой функции
3. Внесите изменения
4. Создайте Pull Request

## 📄 Лицензия

Этот проект распространяется под лицензией MIT.

## ⚠️ Важные замечания

- Скрипт делает запросы к API hirehi.ru с задержками
- Не злоупотребляйте частотой запросов
- Данные обновляются только при запуске скрипта
- GitHub Pages версия статическая (обновляется через Git)