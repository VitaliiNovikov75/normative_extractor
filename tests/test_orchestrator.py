# tests/test_orchestrator.py
import pandas as pd

def test_pipeline_output_format(orchestrator, sample_url):
    df = orchestrator.run_pipeline(sample_url)
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    
    required_columns = ['document', 'text', 'score', 'has_metrics', 'source_url']
    for col in required_columns:
        assert col in df.columns
