# tests/test_engine.py
def test_scoring_engine_accuracy(engine):
    # Тест качественного требования
    high_quality = 'Погрешность прибора должна составлять не более +/- 0.5 мм.'
    assert engine.calculate_score(high_quality) >= 6.0
    
    # Тест шума
    noise = 'Источник публикации М.: ФГБУ Институт стандартизации'
    assert engine.calculate_score(noise) < 0
