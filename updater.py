
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
        
        