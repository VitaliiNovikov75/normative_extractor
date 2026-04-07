# tests/test_loader.py
def test_loader_connectivity(loader, sample_url):
    html = loader.fetch_html(sample_url)
    assert len(html) > 500, 'HTML слишком короткий'
    
    text = loader.extract_clean_text(html)
    assert '<div' not in text, 'В тексте остались HTML-теги'
