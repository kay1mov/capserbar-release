import json, os, sys
from pathlib import Path
from common.utils import Log

class IO:

    @staticmethod
    def LoadJSON(path_to_file: str) -> dict:
        """
        :param path_to_file: Путь к файлу
        :return: JSON Данные
        """
        try:
            with open(path_to_file, mode='r', encoding="utf8") as f:
                content = f.read()
                if not content.strip():
                    Log.WARN("Target file is empty, returning {} as a result")
                    return {}
                return json.loads(content)

        except Exception:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            Log.FATAL((exc_type, exc_value, exc_traceback))

    @staticmethod
    def DumpJSON(obj: dict, file: str):
        """
        :param obj: Объект типа Dict
        :param file: Имя файла или путь к файлу
        :return: Нечего
        """
        try:


            with open(file, mode="w", encoding="utf8") as f:
                json.dump(obj, f, ensure_ascii=True, indent=4)
        except Exception:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            Log.FATAL((exc_type, exc_value, exc_traceback))

    @staticmethod
    def CreateFile(filename: str, filepath: str):
        """
        :param filename: Имя файла включая расширение
        :param filepath: Путь к директории файла
        :return: Нечего
        """

        Log.INFO(f"Incoming data: {filename} and {filepath}")
        try:
            open(f"{filepath}\\{filename}", mode="w")
            Log.INFO(f"Successfully created {filename} in {filepath}")
        except Exception:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            Log.FATAL((exc_type, exc_value, exc_traceback))
    @staticmethod
    def RemoveFile(path_to_file: str):
        """
        :param path_to_file: Путь к файлу
        :return: Нечего
        """
        try:
            Log.INFO(f"Incoming data: {path_to_file}")
            if os.path.exists(path_to_file):
                os.remove(path_to_file)
                Log.INFO(f"Successfully removed {path_to_file}")
            else:
                Log.ERROR(f"{path_to_file} not found")
                raise FileNotFoundError(f"{path_to_file} не найден.")
        except Exception:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            Log.FATAL((exc_type, exc_value, exc_traceback))

    @staticmethod
    def EnsureFileExists(path: Path, default_data: dict | None = None) -> None:
        try:
            Log.INFO(f"Incoming data; {str(path)}, {default_data}")
            if default_data is None:
                default_data = {}
                Log.WARN("Default data is empty")
            if not path.exists():
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(default_data, f, indent=4, ensure_ascii=False)
                    Log.INFO("Successfully dumped")
        except Exception:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            Log.FATAL((exc_type, exc_value, exc_traceback))
    @staticmethod
    def GetValue(path: Path, *keys, default=None):
        try:
            Log.INFO(f"Incoming data: {str(path)}, {str(*keys)}, {str(default)}")
            data = IO.LoadJSON(path)
            for key in keys:
                if isinstance(data, dict) and key in data:
                    data = data[key]
                else:
                    Log.WARN(f"Incorrect isinstance for {key} ({str(type(key))}, returned None")
                    return default

            Log.INFO(f"Successfully returned {data}")
            return data
        except Exception:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            Log.FATAL((exc_type, exc_value, exc_traceback))