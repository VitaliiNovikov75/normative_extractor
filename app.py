# app.py
import streamlit as st
import pandas as pd
import requests
import time
from io import StringIO

from src.utils.loader import MeganormLoader
from src.core.processor import TextProcessor
from src.core.engine import ScoringEngine
from src.core.orchestrator import NormativeOrchestrator
from src.utils.visual import Visualizer

st.set_page_config(page_title='Экстрактор знаний', page_icon='📋')
st.title('Экстрактор знаний и нормативных требований')

# Инициализация
if 'loader' not in st.session_state:
    st.session_state.loader = MeganormLoader()
    st.session_state.processor = TextProcessor()
    st.session_state.engine = ScoringEngine()
    st.session_state.orchestrator = NormativeOrchestrator(
        st.session_state.loader,
        st.session_state.processor,
        st.session_state.engine
    )
    st.session_state.viz = Visualizer()
    st.session_state.raw_docs = {}
    st.session_state.processed_docs = {}
    st.session_state.refined_results = {}
    st.session_state.results_df = None
    st.session_state.stats_df = None

# Создаем вкладки
tab1, tab2 = st.tabs(['Извлечение', 'Аналитика'])


# Вкладка 1: Извлечение
with tab1:
    url = st.text_input('Введите URL документа:', placeholder='https://meganorm.ru/...')

    if st.button('Извлечь'):
        if url:
            with st.spinner('Обработка...'):
                try:
                    # Загрузка данных
                    html = st.session_state.loader.fetch_html(url)
                    raw_text = st.session_state.loader.extract_clean_text(html)

                    st.session_state.raw_docs[url] = raw_text

                    clean_text = st.session_state.processor.clean_garbage(raw_text)
                    sentences = st.session_state.processor.split_to_sentences(clean_text)
                    st.session_state.processed_docs[url] = sentences

                    df = st.session_state.orchestrator.run_pipeline(url)

                    if not df.empty:
                        st.success(f'Найдено требований: {len(df)}')

                        # Накопление результатов
                        if st.session_state.results_df is None:
                            st.session_state.results_df = df
                        else:
                            st.session_state.results_df = pd.concat([st.session_state.results_df, df], ignore_index=True)

                        st.session_state.refined_results[url] = df['text'].tolist()

                        # Статистика для графиков
                        doc_name = st.session_state.processor.extract_document_name(raw_text[:5000])
                        if doc_name == 'Unknown Document':
                            name_parts = url.split('/')[-1].split('_')
                            doc_name = f'{name_parts[0].upper()} {name_parts[1]}'

                        stats_data = [{
                            'Документ': doc_name,
                            'Символы, шт.': len(raw_text),
                            'Размер, кб.': int(len(raw_text) / 1024)
                        }]
                        st.session_state.stats_df = pd.DataFrame(stats_data)

                        st.subheader('Примеры требований:')
                        st.dataframe(df.sample(min(5, len(df)))[['text', 'score', 'has_metrics']])

                    else:
                        st.warning('Требования не найдены')

                except Exception as e:
                    st.error(f'Ошибка: {str(e)}')
        else:
            st.warning('Введите URL')

    if st.session_state.results_df is not None and not st.session_state.results_df.empty:
        st.subheader('Сохранить результаты')

        csv = st.session_state.results_df.to_csv(index=False, encoding='utf-8-sig')
        st.download_button(
            label='Скачать CSV',
            data=csv,
            file_name=f'requirements_{time.strftime("%Y%m%d_%H%M%S")}.csv',
            mime='text/csv'
        )

        if st.button('Очистить все данные', type='secondary'):
            st.session_state.raw_docs = {}
            st.session_state.processed_docs = {}
            st.session_state.refined_results = {}
            st.session_state.results_df = None
            st.session_state.stats_df = None
            st.success('Все данные очищены')
            st.rerun()


# Вкладка 2: Аналитика
with tab2:
    if st.session_state.results_df is not None and not st.session_state.results_df.empty:
        if st.session_state.raw_docs:
            st.subheader(' ')
            st.session_state.viz.plot_download_metrics(
                st.session_state.raw_docs,
                st.session_state.processor
            )

        if st.session_state.processed_docs:
            st.subheader(' ')
            st.session_state.viz.plot_document_distribution(
                st.session_state.processed_docs,
                st.session_state.processor
            )

        if st.session_state.processed_docs and st.session_state.refined_results:
            st.subheader(' ')
            st.session_state.viz.plot_filter_efficiency(
                st.session_state.processed_docs,
                st.session_state.refined_results,
                st.session_state.processor
            )
        st.subheader(' ')
        st.session_state.viz.plot_extraction_quality(st.session_state.results_df)

        st.subheader('Статистика')
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric('Всего требований', len(st.session_state.results_df))
        with col2:
            st.metric('Средняя оценка', f'{st.session_state.results_df["score"].mean():.2f}')
        with col3:
            st.metric('Максимальная оценка', f'{st.session_state.results_df["score"].max():.2f}')

    else:
        st.info('Нет данных для аналитики, сначала извлеките требования')
