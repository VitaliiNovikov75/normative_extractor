# main.py
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl
from typing import List, Dict
import httpx  # Для обработки ошибок

from src.core.processor import TextProcessor
from src.core.engine import ScoringEngine
from src.core.orchestrator import NormativeOrchestrator
from src.utils.loader import MeganormLoader

app = FastAPI(
    title="API для извлечения нормативных знаний",
    description="API для автоматического извлечения требований из документов и ГОСТов.",
    version="1.0.0"
)

loader = MeganormLoader()
processor = TextProcessor()
engine = ScoringEngine()
orchestrator = NormativeOrchestrator(loader, processor, engine)

# Модели запросов/ответов
class ExtractionRequest(BaseModel):
    """Схема входных данных для API"""

    url: HttpUrl

class APIRequirement(BaseModel):
    """Схема отдельного требования в ответе"""

    text: str
    score: float
    has_metrics: bool

class ExtractionResponse(BaseModel):
    """Схема успешного ответа API"""

    status: str = 'success'
    document_name: str
    found_count: int
    data: List[APIRequirement]

# Эндпоинты
@app.get('/')
def read_root():
    return {'message': 'Привет друг!'}

@app.get('/health', tags=['System'])
async def health_check():
    """Проверка доступности сервиса"""

    return {'status': 'alive', 'engine': 'ready'}

@app.post('/extract', response_model=ExtractionResponse, tags=['Extraction'])
async def extract_norms(request: ExtractionRequest):
    """
    Основной эндпоинт для извлечения требований.

    Прием URL, прогон через Orchestrator и возврат структурированного JSON с результатами.
    """

    try:
        df = orchestrator.run_pipeline(str(request.url))

        if df.empty:
            raise HTTPException(status_code=404, detail='Требования в документе не найдены')

        # DataFrame в список объектов для API
        items = [
            APIRequirement(
                text=row['text'],
                score=float(row['score']),
                has_metrics=bool(row['has_metrics'])
            ) for _, row in df.iterrows()
        ]

        return ExtractionResponse(
            document_name=df['document'].iloc[0],
            found_count=len(items),
            data=items
        )

    except httpx.HTTPStatusError as e:
        # Обработка HTTP ошибок
        raise HTTPException(
            status_code=400,
            detail=f'Документ не найден: {str(e)}'
        )
    except httpx.RequestError as e:
        # Обработка сетевых ошибок
        raise HTTPException(
            status_code=400,
            detail=f'Ошибка подключения: {str(e)}'
        )
    except Exception as e:
        # Возврат ошибки, а не 500
        raise HTTPException(status_code=500, detail=f'Ошибка обработки: {str(e)}')

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)
