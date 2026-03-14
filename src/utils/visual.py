# src/utils/visual.py
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from typing import List, Dict, Optional
import streamlit as st

class Visualizer:
    """
    Класс для визуализации результатов анализа нормативных документов.

    Методы:
    - plot_download_metrics() - метрики загрузки документов
    - plot_document_distribution() - доля предложений по документам
    - plot_filter_efficiency() - эффективность лингвистического фильтра
    - plot_extraction_quality() - ранжирование требований
    """

    def __init__(self, style: str = 'seaborn-v0_8-whitegrid'):
        """
        Инициализация визуализатора с настройками стиля.

        Args:
            style: Стиль matplotlib для графиков
        """

        self.style = style
        self.colors = {
            'primary': '#3498db',
            'secondary': '#e74c3c',
            'success': '#2ecc71',
            'warning': '#f1c40f',
            'gray': '#95a5a6',
            'light': '#bdc3c7',
            'dark': '#2c3e50'
        }
        self.doc_colors = ['#3498db', '#2ecc71', '#f1c40f', '#e74c3c']

    def _clean_spines(self, ax: plt.Axes) -> None:
        """Убирает верхнюю и правую границы графика."""

        for spine in ['top', 'right']:
            ax.spines[spine].set_visible(False)

    def plot_download_metrics(self, raw_docs: Dict[str, str], processor) -> None:
        """
        График 1: Метрики загрузки документов.

        Args:
            raw_docs: Словарь {url: текст документа}
            processor: Экземпляр TextProcessor для извлечения имен
        """

        stats_data = []
        for url, text in raw_docs.items():
            # Иимя документа через processor
            doc_name = processor.extract_document_name(text[:5000])
            if doc_name == 'Unknown Document':
                # Запасной вариант из URL
                name_parts = url.split('/')[-1].split('_')
                doc_name = f'{name_parts[0].upper()} {name_parts[1]}'

            char_count = len(text)
            kb_size = int(char_count / 1024)

            stats_data.append({
                'Документ': doc_name,
                'Символы, шт.': char_count,
                'Размер, кб.': kb_size
            })

        df_stats = pd.DataFrame(stats_data)

        plt.figure(figsize=(11, 6))
        bars = plt.bar(
            df_stats['Документ'], df_stats['Размер, кб.'],
            color=self.colors['primary'],
            alpha=0.85,
            width=0.5)
        plt.xlabel('Документ', fontsize=11, fontweight='bold')
        plt.ylabel('Размер, кб.', fontsize=11, fontweight='bold')
        plt.title('Метрики загрузки документов',
                  fontsize=15, pad=20, fontweight='bold')
        plt.ylim(0, df_stats['Размер, кб.'].max() * 1.2)

        # Двойные метки
        for bar, char, kb in zip(bars, df_stats['Символы, шт.'], df_stats['Размер, кб.']):
            height = bar.get_height()
            # Основная метка (КБ)
            plt.text(bar.get_x() + bar.get_width()/2., height + 1,
                    f'{kb} кб.', ha='center', va='bottom',
                    fontsize=11, fontweight='bold', color=self.colors['dark'])
            # Дополнительная метка (символы)
            plt.text(bar.get_x() + bar.get_width()/2., height / 2,
                    f'{char}\nсимволов', ha='center', va='center',
                    fontsize=10, color='white', fontweight='bold')

        self._clean_spines(plt.gca())
        plt.gca().yaxis.grid(True, linestyle='--', alpha=0.3)
        plt.gca().xaxis.grid(False)
        plt.tight_layout()
        st.pyplot(plt)
        plt.show()

    def plot_document_distribution(self, processed_docs: Dict[str, List[str]],
                                   processor) -> None:
        """
        График 2: Доля предложений по документам (круговая).

        Args:
            processed_docs: Словарь {url: список предложений}
            processor: Экземпляр TextProcessor для извлечения имен
        """

        labels = []
        sizes = []

        for url, sentences in processed_docs.items():
            full_text = ' '.join(sentences[:100])
            doc_name = processor.extract_document_name(full_text)
            labels.append(doc_name)
            sizes.append(len(sentences))

        plt.figure(figsize=(10, 7))
        wedges, texts, autotexts = plt.pie(
            sizes,
            labels=labels,
            autopct='%1.1f%%',
            startangle=140,
            colors=self.doc_colors[:len(sizes)],
            pctdistance=0.85,
            explode=[0.03] * len(sizes),
            textprops={'fontsize': 12, 'fontweight': 'bold'}
        )

        # Центральный круг для пончика
        centre_circle = plt.Circle((0,0), 0.70, fc='white')
        plt.gca().add_artist(centre_circle)

        total_sentences = sum(sizes)
        plt.text(0, 0, f'{total_sentences}\nсущности',
                 ha='center', va='center', fontsize=14,
                 fontweight='bold', color=self.colors['dark'])

        plt.title('Доля предложений по документам',
                  fontsize=15, pad=20, fontweight='bold')
        plt.axis('equal')
        plt.tight_layout()
        st.pyplot(plt)
        plt.show()

    def plot_filter_efficiency(self, processed_docs: Dict[str, List[str]],
                              refined_results: Dict[str, List],
                              processor) -> None:
        """
        График 3: Эффективность лингвистического фильтра (воронка).

        Args:
            processed_docs: Словарь {url: список предложений}
            refined_results: Словарь {url: список требований}
            processor: Экземпляр TextProcessor для извлечения имен
        """
        
        doc_labels = []
        candidates_counts = []
        requirements_counts = []
        efficiency_rates = []

        for url in processed_docs.keys():
            sentences = processed_docs[url]
            full_text = ' '.join(sentences[:100])
            doc_name = processor.extract_document_name(full_text)

            doc_labels.append(doc_name)

            total = len(processed_docs[url])
            found = len(refined_results[url])

            candidates_counts.append(total)
            requirements_counts.append(found)
            efficiency_rates.append(int((found / total) * 100))

        x = np.arange(len(doc_labels))
        width = 0.4

        fig, ax = plt.subplots(figsize=(12, 7))

        rects1 = ax.bar(
            x - width/2,
            candidates_counts,
            width,
            label='Кандидаты',
            color=self.colors['light'],
            alpha=0.6)
        rects2 = ax.bar(
            x + width/2,
            requirements_counts,
            width,
            label='Требования',
            color=self.colors['secondary'],
            alpha=0.9)

        # Метки с процентом эффективности
        for i, rect in enumerate(rects2):
            height = rect.get_height()
            ax.annotate(f'{efficiency_rates[i]}%',
                        xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(0, 0),
                        textcoords="offset points",
                        ha='center',
                        va='bottom',
                        fontsize=11,
                        fontweight='bold',
                        color='#c0392b',
                        )

        ax.set_ylabel('Количество фрагментов текста', fontsize=12, fontweight='bold')
        ax.set_title('Эффективность лингвистического фильтра',
                     fontsize=15, pad=20, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(doc_labels, fontsize=12)
        ax.legend(fontsize=11)
        ax.yaxis.grid(True, linestyle='--', alpha=0.4)
        ax.xaxis.grid(False)
        self._clean_spines(ax)
        plt.xlabel('Документ', fontsize=11, fontweight='bold')
        plt.tight_layout()
        st.pyplot(plt)
        plt.show()

    def plot_extraction_quality(self, df: pd.DataFrame) -> None:
        """
        График 4: Ранжирование нормативных требований (scatter plot).

        Args:
            df: DataFrame с колонками ['document', 'text', 'score', 'has_metrics']
        """
        if df.empty:
            print('[ERROR] Нет данных для визуализации')
            return

        df_plot = df.copy().reset_index()
        df_plot['ID'] = df_plot.index + 1

        plt.style.use(self.style)
        fig, ax = plt.subplots(figsize=(13, 7))

        # Цвета для разных документов
        unique_docs = df_plot['document'].unique()
        doc_map = {doc: self.doc_colors[i % len(self.doc_colors)]
                   for i, doc in enumerate(unique_docs)}

        for doc in unique_docs:
            subset = df_plot[df_plot['document'] == doc]
            ax.scatter(
                subset['ID'],
                subset['score'],
                s=subset['score'] * 30,
                c=doc_map[doc],
                label=doc,
                alpha=0.65,
                edgecolors='white',
                linewidth=0.5
            )

        # Опорные линии
        ax.axhline(y=6.0, color=self.colors['secondary'], linestyle='--',
                   alpha=0.6, label='Зона высокой точности')
        ax.axhline(y=2.0, color=self.colors['gray'], linestyle=':',
                   alpha=0.4, label='Порог шума')

        ax.set_ylabel('Оценка качества', fontsize=12, fontweight='bold', labelpad=10)
        ax.set_xlabel('Номер требования', fontsize=12, fontweight='bold', labelpad=10)
        ax.set_title('Ранжирование нормативных требований',
                     fontsize=15, pad=20, fontweight='bold')
        ax.legend(frameon=True, loc='upper right', fontsize=10,
                  facecolor='white', framealpha=0.9)
        ax.grid(True, linestyle='--', alpha=0.3)

        self._clean_spines(ax)
        plt.tight_layout()
        st.pyplot(plt)
        plt.show()
