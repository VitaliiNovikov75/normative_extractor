# tests/conftest.py
import sys
# import os
from pathlib import Path

# Корень проекта в sys.path,
# на уровень вверх от tests/
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

import pytest
from src.core.engine import ScoringEngine
from src.utils.loader import MeganormLoader
from src.core.processor import TextProcessor
from src.core.orchestrator import NormativeOrchestrator

@pytest.fixture
def engine():
    return ScoringEngine()

@pytest.fixture
def loader():
    return MeganormLoader()

@pytest.fixture
def processor():
    return TextProcessor()

@pytest.fixture
def orchestrator(loader, processor, engine):
    return NormativeOrchestrator(loader, processor, engine)

@pytest.fixture
def sample_url():
    return 'https://meganorm.ru/mega_doc/norm/gost_gosudarstvennyj-standart/0/gost_34714-2021_ISO_7076-5-2014_mezhgosudarstvennyy_standart.html'
