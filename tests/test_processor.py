# tests/test_processor.py
def test_extract_document_name(processor):
    """Проверка извлечения названия ГОСТ/СП из начала текста."""

    text = 'Текст документа ГОСТ Р 52289-2019 Технические средства организации дорожного движения...'
    assert processor.extract_document_name(text) == 'ГОСТ Р 52289-2019'

    bad_text = 'Просто какой-то текст без номеров стандартов.'
    assert processor.extract_document_name(bad_text) == 'Unknown Document'

def test_clean_garbage(processor):
    """Проверка отсечения навигационного шума до раздела 'Область применения'."""

    raw = 'Меню сайта Контакты Поиск 1 Область применения Данный стандарт устанавливает'
    cleaned = processor.clean_garbage(raw)

    # Должно начинаться с 1 Область
    assert cleaned.startswith('1 Область')
    # Должны исчезнуть лишние пробелы
    assert 'Меню сайта' not in cleaned

def test_split_to_sentences_filter_short(processor):
    """Проверка фильтрации слишком коротких фрагментов (< 35 символов)."""

    short_text = 'Это длинное предложение, которое должно пройти фильтр по длине. А это короткое.'
    sentences = processor.split_to_sentences(short_text)

    assert len(sentences) == 1
    assert 'Это длинное предложение' in sentences[0]
