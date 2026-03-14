import httpx
from selectolax.parser import HTMLParser
from fake_useragent import UserAgent

class MeganormLoader:
    """
    Класс для загрузки и парсинга HTML-документов с meganorm.ru.

    Обеспечивает анонимность запросов через динамические заголовки и
    извлекает чистое текстовое тело документа из DOM-структуры.

    Генерирует правдоподобные заголовки, чтобы сайт не понял, что это робот.

    Заголовки — это как одежда для запроса. Если все запросы будут в одинаковой
    одежде, сайт быстро вычислит бота. Этот класс переодевает каждый запрос
    в случайный костюм Chrome или Edge.
    """

    def __init__(self):
        """Собирает словарь заголовков для HTTP-запроса.

        Returns:
            Словарь с заголовками:
            - User-Agent: случайный браузер
            - Accept: какие форматы файлов поддерживаются
            - Accept-Language: предпочитаемые языки ответа
            - Referer: источник запроса
            - DNT: сигнал "не отслеживать"

        Значения q=0.9, 0.8 в Accept:
            Это весовые коэффициенты предпочтений. Форматы с более высоким q
            запрашиваются в первую очередь. По умолчанию q=1.0.
        """
        self._ua = UserAgent(browsers=['chrome', 'edge'])
        # Заголовки генерируются динамически
        self.headers = {
            'User-Agent': self._ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
            'Referer': 'https://meganorm.ru',
            'DNT': '1'
        }

    def fetch_html(self, url: str) -> str:
        """Выполняет HTTP GET запрос и возвращает HTML-контент.

        Args:
            url: Целевой URL для загрузки

        Returns:
            HTML-код страницы в виде строки

        Raises:
            httpx.HTTPStatusError: При статус-коде >= 400
            httpx.RequestError: При сетевых ошибках

        Description:
            - Автоматически следует редиректам
            - Использует заголовки из HeaderProvider
        """
        print(f'[INFO] Запрос к {url}')
        # Использую follow_redirects=True, meganorm часто переходит на актуальные версии
        with httpx.Client(headers=self.headers, follow_redirects=True, timeout=15.0) as client:
            response = client.get(url)
            response.raise_for_status()
            return response.text

    def extract_clean_text(self, html: str) -> str:
        """Извлекает чистый текст из HTML, удаляя технические элементы.

        Args:
            html: Сырой HTML-код страницы

        Returns:
            Текст документа с разделением строк

        Description:
            1. Поиск контейнера с контентом (div.text_doc → article → body)
            2. Удаление script, style, ins, ads
            3. Извлечение текста с сохранением структуры абзацев
        """
        tree = HTMLParser(html)

        # На meganorm основной контент обычно лежит в div с определенным id или классом.
        # Поиск центрального блока текста. Если селектор не сработает, выбор body
        content_node = tree.css_first('div.text_doc') or tree.css_first('article') or tree.css_first('body')

        if not content_node:
            return ""

        # Удаляю скрипты и стили, чтобы они не попали в сегментацию
        for tag in content_node.css('script, style, ins, ads'):
            tag.decompose()

        # Использую сепаратор '\n', чтобы сохранить границы строк перед чисткой
        return content_node.text(separator='\n', strip=True)
