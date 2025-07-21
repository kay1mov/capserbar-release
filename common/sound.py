import pygame, winsound, random, sys
from config import *
from common.utils import Log
import threading

class Play:

    """
    Мастер по воспроизведении звука из любого звукового файла
    """

    @staticmethod
    def PlaySound(path_to_sound: str, sfx_only: bool = True, category: str = ""):

        """
        :param path_to_sound: Путь к звуку
        :param sfx_only: Только из SFX
        :param category: Категория звука
        :return: Нечего
        """
        try:
            Log.INFO(f"Playsound for {path_to_sound} | sfx: {sfx_only} | category: {category}")
            if sfx_only: path = f"data\\sfx\\{category}\\{path_to_sound}"
            else: path = path_to_sound
            pygame.init()
            pygame.mixer.init()
            threading.Thread(
                target=lambda: (
                    pygame.mixer.music.load(path),
                    pygame.mixer.music.play(),
                    [pygame.time.Clock().tick(10) for _ in iter(lambda: pygame.mixer.music.get_busy(), False)]
                ),
                daemon=True
            ).start()
        except Exception:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            Log.FATAL((exc_type, exc_value, exc_traceback))
    @staticmethod
    def PlayCustomSound(frequency: int, duration: float):   
        """
        :param frequency: Частота звука
        :param duration: Длительность воспроизведения
        :return: Нечего
        """
        try:
            Log.INFO(f"Playing custom sound with {frequency}HZ for {duration} milliseconds")
            threading.Thread(target=lambda: winsound.Beep(frequency, duration), daemon=True).start()
        except Exception:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            Log.FATAL((exc_type, exc_value, exc_traceback))
class Master:
    """
    Мастер по воспроизведению звука
    Play <- (category, number, rnd) -> Воспроизведение звука
    """

    @staticmethod
    def Play(category: str, number: int = 0, rnd: bool = True):
        """
        :param category: Название категории звука
        :param number: Номер звукового файла
        :param rnd: воспроизводить случайно?
        :return: Нечего
        """

        try:
            Log.INFO(f"Playing for sound through master, {category} | #{number} | random = {rnd}")
            if number != 0: rnd = False
            path = SFX_DIR / category
            if not path.exists() or not path.is_dir():
                Log.FATAL(f"Fatal error, directory {path} not found!")
                raise FileNotFoundError(f"Directory '{path}' not found.")

            sound_files = [f for f in path.glob("*.mp3")]
            if not sound_files:
                Log.FATAL(f"Fatal error, in {path} no .mp3 files")
                raise FileNotFoundError(f"No .mp3 files in {path}")

            if rnd:
                sound = random.choice(sound_files)
            else:
                try:
                    sound = sound_files[number - 1]
                except IndexError:
                    Log.FATAL(f"There no .mp3 file with index {number} in {path}")
                    raise FileNotFoundError(f"No .mp3 file at index {number - 1} in {path}")

            Play.PlaySound(str(sound), False)
        except Exception:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            Log.FATAL((exc_type, exc_value, exc_traceback))