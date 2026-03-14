import pandas as pd

class NormativeOrchestrator:
    """
    Класс-оркестратор для управления полным циклом извлечения знаний.

    Связывает компоненты загрузки, обработки и оценки в единый конвейер.
    Обеспечивает вывод результатов в форматах DataFrame и Pydantic-моделей.
    """

    def __init__(self, loader, processor, engine):
        """
        Инициализация оркестратора компонентами системы.

        Аргументы:
            loader: Экземпляр класса для загрузки HTML (MeganormLoader).
            processor: Экземпляр класса для обработки текста (TextProcessor).
            engine: Экземпляр класса для оценки релевантности (ScoringEngine).
        """
        self.loader = loader
        self.processor = processor
        self.engine = engine

    def _get_doc_name(self, text: str) -> str:
        """Использует processor.extract_document_name для поиска имени"""

        return self.processor.extract_document_name(text)

    def run_pipeline(self, url: str) -> pd.DataFrame:
        """
        Запускает полный цикл извлечения требований для одного URL.

        Аргументы:
            url (str): Ссылка на документ meganorm.ru.

        Возвращает:
            pd.DataFrame: Отсортированная таблица с извлеченными требованиями.
        """
        # Загрузка данных
        html = self.loader.fetch_html(url)
        raw_text = self.loader.extract_clean_text(html)

        # Динамическое определение имени
        doc_name = self._get_doc_name(raw_text)

        # Очистка и сегментация
        clean_text = self.processor.clean_garbage(raw_text)
        sentences = self.processor.split_to_sentences(clean_text)

        # Анализ и скоринг
        extracted_data = []
        for sent in sentences:
            score = self.engine.calculate_score(sent)

            # Порог качества
            if score >= 2.5:
                extracted_data.append({
                    'document': doc_name,
                    'text': sent,
                    'score': score,
                    'has_metrics': self.engine.has_metrics(sent),
                    'source_url': url
                })

        # Финальный DataFrame
        df = pd.DataFrame(extracted_data)
        if not df.empty:
            return df.sort_values(by='score', ascending=False).reset_index(drop=True)
        return df
