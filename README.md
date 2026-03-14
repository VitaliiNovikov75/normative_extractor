# Экстрактор нормативов
Архитектура на основе методов анализа текста, которая извлекает из документов нормативы и указания на требования с сайта [meganorm.ru](http://meganorm.ru) Проект включает:
- **python** язык, на котором написана архитектура;
- **backend** на FastAPI для обработки документов;
- **frontend UI** на streamlit для удобного взаимодействия;
- **ядро системы** с лингвистическим анализом и скорингом требований;
- **аналитику** требований с помощью matplotlib;
- **docker** для простого развертывания.
# Структура проекта
```
├── data/                     # локальное хранилище
│   ├── raw/                  # сырые загруженные файлы
│   └── processed/            # извлеченные структурированные знания
├── src/                      # исходный код
│   ├── __init__.py
│   ├── api/                  # backend слой
│   │   ├── __init__.py
│   │   └── main.py           # точка входа API
│   ├── core/                 # ядро системы
│   │   ├── __init__.py
│   │   ├── engine.py         # оценка релевантности предложений 
│   │   ├── processor.py      # очистка и сегментация текста
│   │   ├── orchestrator.py   # связывает компоненты в единый цикл
│   │   └── models.py         # pydantic модели
│   └── utils/                # вспомогательный код
│       ├── loader.py         # работа с http/selectolax
│       └── visual.py         # визуализация результатов
├── tests/                    # юнит-тесты
│   ├── conftest.py           # фикстуры
│   ├── test_engine.py        # тест ScoringEngine
│   ├── test_orchestrator.py  # тест NormativeOrchestrator
│   ├── test_processor.py     # тест TextProcessor
│   └── test_loader.py        # тест MeganormLoader
├── research/                 # исследовательская часть
│       └── description.ipynb
├── docs/                     # документация sphinx
├── .gitignore
├── Dockerfile                # инструкция сборки образа
├── .dockerignore
├── docker-compose.yml        # оркестрация API + UI + docs
├── requirements.txt          # зависимости python
├── app.py                    # streamlit приложение
├── LICENSE
└── README.md
```
# Основные результаты исследования
Приступая к выполнению тестового задания (подробности в [description.ipynb](https://github.com/VitaliiNovikov75/normative_extractor/blob/main/research/description.ipynb)) я принял решение использовать максимально легкие и быстрые библиотеки, чтобы обеспечить минимальную задержку, надежную броню и 100% предсказуемость по паттернам RegEx. Уверен, что нет смысла сразу использовать языковые модели. Ведь они требуют большого количества ресурсов для инференса, которые всегда ограничены.

Итог очевиден и краток: RegEx — высокопроизводительное ядро системы. А LLM — интеллектуальная надстройка для сложного контекста.
## Анализ эффективности линвистического фильтра
Для оценки работы алгоритма был проведен анализ четырех нормативных документов. График ниже иллюстрирует соотношение общего количества найденных кандидатов (серый цвет) к реально подтвержденным требованиям (красный цвет).
**Основные выводы:**
- **Высокая селективность**: Алгоритм эффективно сокращает объем данных для анализа, отсеивая от **52% до 71%** нерелевантных фрагментов текста.
- **Стабильность на разных объемах**: Фильтр одинаково эффективно работает как с небольшими документами до 150 фрагментов, так и с объемными стандартами.
- **Оптимизация**: Использование лингвистического фильтра позволяет сфокусировать внимание пользователя (или последующих моделей обработки) только на **29–48%** текста, который действительно содержит нормативные предписания.
<p align="center">
  <img src="data/1.png" width="1000" alt="Описание">
</p>

# Запуск
## В Windows через docker
```powershell
git clone https://github.com/VitaliiNovikov75/normative_extractor.git
cd C:\Users\пользователь\Desktop\normative_extractor

docker compose -p normative_extractor up -d

docker exec normative_extractor-api-1 sphinx-build -b html docs/source docs/build/html
```
## Linux
### Через окружение python
```bash
git clone https://github.com/VitaliiNovikov75/normative_extractor.git
cd normative_extractor

python -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt

streamlit run app.py &

cd docs
make html
cd build/html
python -m http.server 8080
```
### Через docker
```bash
git clone https://github.com/VitaliiNovikov75/normative_extractor.git
cd normative_extractor

sudo systemctl start docker
docker compose -p normative_extractor up -d --build

docker exec normative_extractor-api-1 sphinx-build -b html docs/source docs/build/html
```
## Доступ к сервисам
- Streamlit UI: [localhost:8501](http://localhost:8501);
- API: [localhost:8000](http://localhost:8000/);
- swagger API Docs: [localhost:8000/docs](http://localhost:8000/docs);
- sphinx тех. документация: [localhost:8080](http://localhost:8080).
# Использование
1. Откройте [localhost:8501](http://localhost:8501);
2. введите URL документа;
3. нажмите "Извлечь";
4. сохраните результаты через "Скачать в CSV" либо "Очистить все данные".
# Функциональность
## Вкладка "Извлечение"
- Ввод URL документа;
- извлечение требований с отображением примеров;
- скачивание результатов в CSV
- очистка всех данных
## Вкладка "Аналитика"
- Метрики загрузки — размер документов в КБ и количество символов;
- доля предложений — распределение по документам;
- эффективность фильтра — сравнение кандидатов и требований;
- ранжирование требований — scatter plot с оценкой качества;
- статистика — общее количество, средний и максимальный score.
# Стек
- FastAPI — веб-фреймворк;
- uvicorn — асинхронный веб-сервер;
- re — паттерны извлечения требований;
- streamlit — интерактивный UI для данных;
- pydantic — валидация данных;
- pandas — обработка табличных данных;
- matplotlib — визуализация;
- selectolax — быстрый HTML парсер;
- docker — контейнеризация;
- numpy — библиотека для научных вычислений;
- httpx — для запросов;
- fake_useragent — генерация строк User-Agent;
- sphinx — документация.
