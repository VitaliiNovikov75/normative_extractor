Добро пожаловать в документацию Экстрактор нормативов
=====================================================

Система для автоматического извлечения нормативных требований
из документов ГОСТ, СП с сайта meganorm.ru.

.. toctree::
   :maxdepth: 2
   :caption: Содержание:

   installation
   modules
   api

Установка и запуск
------------------

.. code-block:: bash

   # Установка зависимостей
   pip install -r requirements.txt

   # Запуск Streamlit UI
   streamlit run app.py

Архитектура проекта
-------------------

- **src/api** — FastAPI бэкенд
- **src/core** — ядро системы (Requirement, ScoringEngine, TextProcessor, NormativeOrchestrator)
- **src/utils** — утилиты (загрузчик, визуализация)
- **app.py** — Streamlit интерфейс

Индексы и таблицы
-----------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
