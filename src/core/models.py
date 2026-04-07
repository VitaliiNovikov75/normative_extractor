from pydantic import BaseModel, Field
from typing import List

class Requirement(BaseModel):
    """
    Класс, представляющий отдельное нормативное требование.

    Atributs:
        text (str): Исходный текст извлеченного требования.
        score (float): Балл релевантности, рассчитанный ScoringEngine.
        has_metrics (bool): Флаг, указывающий на наличие физических величин в тексте.
        source_url (str): Ссылка на исходный документ meganorm.ru.
    """
    text: str = Field(..., description='Исходный текст извлеченного требования')
    score: float = Field(..., description='Балл релевантности, рассчитанный ScoringEngine')
    has_metrics: bool = Field(..., description='Флаг, наличия физических величин')
    source_url: str = Field(..., description='Ссылка на документ')

class ExtractionResult(BaseModel):
    """
    Контейнер для результатов обработки целого документа.

    Atributs:
        document_name (str): Официальное наименование документа (например, ГОСТ 34714).
        requirements (List[Requirement]): Список всех валидных требований, прошедших порог.
        total_found (int): Общее количество найденных требований.
    """
    document_name: str = Field(..., description='Официальное наименование документа')
    requirements: List[Requirement] = Field(default_factory=list, description='Список извлеченных знаний')
    total_found: int = Field(..., description='Общее количество найденных требований')

    class Config:
        """Настройки для работы с DataFrame и JSON."""
        arbitrary_types_allowed = True
        json_schema_extra = {
            'example': {
                'document_name': 'ГОСТ 34714-2021',
                'requirements': [],
                'total_found': 10
            }
        }
