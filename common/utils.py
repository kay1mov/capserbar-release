import hashlib, sys, logging
from config import DATA_DIR

class Log:
    _logger = None
    _initialized = False

    @classmethod
    def _init_logger(cls):

        """Инициализация логгера при первом использовании"""
        if cls._initialized:
            return

        cls._logger = logging.getLogger('AppLogger')
        cls._logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(module)s - %(funcName)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        # Обработчик для файла
        log_filename = DATA_DIR / "log.log"
        file_handler = logging.FileHandler(log_filename, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)

        # Обработчик для консоли
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)

        # Добавляем обработчики
        cls._logger.addHandler(file_handler)
        cls._logger.addHandler(console_handler)

        cls._initialized = True

    @classmethod
    def DEBUG(cls, message=""):
        cls._init_logger()
        cls._logger.debug(message, stacklevel=2)  # И так для всех методов

    @classmethod
    def INFO(cls, message=""):
        """Логирование информационных сообщений"""
        cls._init_logger()
        cls._logger.info(message, stacklevel=2)

    @classmethod
    def WARN(cls, message=""):
        """Логирование предупреждений"""
        cls._init_logger()
        cls._logger.warning(message, stacklevel=2)

    @classmethod
    def WARNING(cls, message=""):
        """Альтернативный метод для предупреждений"""
        cls.WARN(message)

    @classmethod
    def ERROR(cls, message=""):
        """Логирование ошибок"""
        cls._init_logger()
        cls._logger.error(message, stacklevel=2)

    @classmethod
    def CRITICAL(cls, message=""):
        """Логирование критических ошибок"""
        cls._init_logger()
        cls._logger.critical(message, stacklevel=2)

    @classmethod
    def FATAL(cls, message=""):
        """Альтернативный метод для критических ошибок"""
        cls.CRITICAL(message)




class Security:

    @staticmethod
    def _get_default_manager_password() -> str:
        Log.INFO()
        return "2e89069808a8d4eef9179d7ef8a4adf6b66d59e3cc07ac8f36f8cf0f31eb0b9154f2e537f21d5d2ff4921cec2d93995ca462149028bef4483b5f7bd9464c7a74"

    @staticmethod
    def _password_to_sha512_hex(password: str):
        try:
            hash_object = hashlib.sha512(password.encode('utf-8'))
            hash_bytes = hash_object.digest()
            hash_hex = hash_bytes.hex()
            Log.INFO()
            return hash_hex
        except Exception:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            Log.FATAL((exc_type, exc_value, exc_traceback))

    @staticmethod
    def _security_notify(account_name: str, password: str):
        Log.WARN(f"Неудачная попытка входа в аккаунт {account_name} с паролем: {password}")

    @staticmethod
    def IsPasswordRight(password: str, account: str) -> bool:
        try:
            from common.io import IO

            _real_pass = password
            password = Security._password_to_sha512_hex(password)
            Log.INFO()
            try:
                selected_password = IO.LoadJSON(DATA_DIR / "common.json")["accounts"].get(account, Security._get_default_manager_password())
                if selected_password == "-": return True
            except Exception as e:
                print(f"Ошибка {e}")
                selected_password = Security._get_default_manager_password()
            if str(password) == str(selected_password): return True

            Security._security_notify(account, _real_pass)
            return False
        except Exception:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            Log.FATAL((exc_type, exc_value, exc_traceback))

