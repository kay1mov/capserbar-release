from common.io import IO
from config import LOCALIZATION_FILE

class Translator:
    def __init__(self, locale: str):
        print(f"Инициализация переводчика для локали: {locale}")
        self.locale = locale
        self.data = {}

        if self.locale != "ru":
            # 1. Загружаем JSON как обычно
            raw_data = IO.LoadJSON(LOCALIZATION_FILE)
            if raw_data:
                # 2. Создаем новый словарь, где все ключи в нижнем регистре
                self.data = {key.lower(): value for key, value in raw_data.items()}

    def __call__(self, text: str) -> str:
        """Этот метод позволяет вызывать экземпляр класса как функцию: _("текст")"""
        if self.locale == "ru" or not self.data:
            return text

        # Теперь поиск по text.lower() всегда будет работать корректно
        return self.data.get(text.lower(), text)