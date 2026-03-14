# docs/source/conf.py
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.abspath('../../'))

project = 'Экстрактор нормативов'
copyright = '2026, Виталий Новиков'
author = 'Виталий Новиков'
release = '1.0.0'

extensions = [
    'sphinx.ext.autodoc',           # Автодокументация из докстрингов
    'sphinx.ext.napoleon',          # Поддержка Google/NumPy стиля
    'sphinx.ext.viewcode',          # Ссылки на исходный код
    'sphinx.ext.githubpages',       # Публикация на GitHub Pages
    'sphinx_autodoc_typehints',     # Поддержка type hints
    'sphinx.ext.todo',              # TODO заметки
    'sphinx.ext.coverage',          # Покрытие документацией
]

# Настройки napoleon для моих докстрингов
napoleon_google_docstring = True
napoleon_numpy_docstring = False
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_param = True
napoleon_use_rtype = True

templates_path = ['_templates']
exclude_patterns = []

language = 'ru'

html_theme = 'sphinx_rtd_theme'
html_theme_options = {
    'navigation_depth': 4,
    'collapse_navigation': False,
    'sticky_navigation': True,
}

html_static_path = ['_static']
