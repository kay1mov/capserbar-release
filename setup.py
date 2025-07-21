import os, json, sys
import time
from pathlib import Path

first = False

class Setup:


    @staticmethod
    def CreateUpdater():
        global first
        CODE = """
import requests
import json
import os
from tqdm import tqdm
# === НАСТРОЙКИ ===
GITHUB_USER = "kay1mov"
REPO_NAME = "capserbar-release"
BRANCH = "refs/heads/main"
MANIFEST_PATH = "manifest.json"

RAW_BASE = f"https://raw.githubusercontent.com/{GITHUB_USER}/{REPO_NAME}/{BRANCH}/"
MANIFEST_URL = RAW_BASE + MANIFEST_PATH

def download_file(file_path):
    url = RAW_BASE + file_path
    local_path = os.path.join(".", file_path)
    os.makedirs(os.path.dirname(local_path), exist_ok=True)

    try:
        r = requests.get(url)
        if r.status_code == 200:
            with open(local_path, 'wb') as f:
                f.write(r.content)
        else:
            print(f"✗ Ошибка 404: {file_path}")
    except Exception as e:
        print(f"✗ Ошибка при загрузке {file_path}: {e}")

def update_from_manifest():
    try:
        print("🔄 Загружаю манифест...")
        print(MANIFEST_URL)
        r = requests.get(MANIFEST_URL)
        if r.status_code != 200:
            print("✗ Не удалось получить manifest.json")
            return

        data = json.loads(r.text)
        file_list = data["path"]
        actual_version = data["__version__"]
        with open("info.json", mode="r", encoding="utf8") as f:
            local_data = json.load(f)

        local_version = local_data["version"]

        if actual_version > local_version:
            print(f"Обнаружена новая версия программы {actual_version}")
            print("Установка...")
            data = {"version": actual_version}
            with open("info.json", mode="w", encoding="utf8")  as f: json.dump(data, f, indent=4)
        else:
            print("Обновления не найдены.")
            return

        print(f"📦 Найдено файлов: {len(file_list)}")
        os.system('pip install tqdm')
        for path in tqdm(file_list, desc="Обновление"):
            download_file(path)

        print("✅ Обновление завершено.")
    except Exception as e:
        print(f"✗ Ошибка при работе с манифестом: {e}")

if __name__ == "__main__":
    update_from_manifest()
        
        """

        with open("updater.py", encoding="utf8", mode="w") as f:
            print("Создание Updater'а")
            f.write(CODE)

    @staticmethod
    def InstallRequirements():
        try:
            os.system(f"{sys.executable} -m pip install -r requirements.txt")
        except Exception as e:
            print(f"Ошибка при установке зависимостей: {e}")
            print(f"Попытка скачивания №2")

            inner = """
babel==2.17.0
certifi==2025.7.14
charset-normalizer==3.4.2
click==8.2.1
colorama==0.4.6
customtkinter==5.2.2
darkdetect==0.8.0
idna==3.10
packaging==25.0
pygame==2.6.1
python-dotenv==1.1.1
requests==2.32.4
shiboken6==6.9.1
tkcalendar==1.6.1
tqdm==4.67.1
urllib3==2.5.0
            """

            with open("requirements.txt", mode="w", encoding="utf8") as f:
                f.write(inner)

            time.sleep(1)
            os.system(f"{sys.executable} -m pip install -r requirements.txt")

    @staticmethod
    def CreatingNewFiles():
        BASE_DIR = Path(__file__).resolve().parent
        DATA_DIR = BASE_DIR / "data"

        files = {
            BASE_DIR / "info.json": {"version": 1000},
            BASE_DIR / "manifest.json": {"__version__": 1000},
            DATA_DIR / "storage.json": {},
            DATA_DIR / "sales.json": {}
        }

        for file, value in files.items():
            if not file.exists():
                file.parent.mkdir(parents=True, exist_ok=True)
                with file.open(mode="w", encoding="utf8") as f:
                    json.dump(value, f, indent=4)

    @staticmethod
    def StartUpdater():
        os.system("python updater.py")


if __name__ == "__main__":

    print("Шаг №1 - Установка зависимостей")
    Setup.InstallRequirements()
    print("Шаг №2 - Созданий важных файлов")
    Setup.CreatingNewFiles()
    print("Шаг №3 - Создание установщика")
    Setup.CreateUpdater()
    print("Шаг №4 - Запуск установщика")
    time.sleep(1)
    Setup.StartUpdater()
    input("УСТАНОВКА ЗАВЕРШЕНА")