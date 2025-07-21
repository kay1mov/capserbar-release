import os

class Setup:

    @staticmethod
    def InstallingRequirements(filepath="requirements.txt"):
        print("УСТАНОВКА ЗАВИСИМОСТЕЙ")
        try:

            os.system(f"pip install -r {filepath}")

        except Exception as e:
            print(f"Ошибка при скачивании зависимостей: \n{e}")

            libs = [
                "customtkinter", "tkcalendar", "colorama", "pygame"
            ]

            print("УСТАНОВКА ЗАВИСИМОСТЕЙ #2")
            try:

                for lib in libs:
                    os.system(f"pip install {lib}")

            except Exception as e:
                print(f"Ошибка при скачивании зависимостей: \n{e}")


if __name__ == "__main__":
    Setup.InstallingRequirements()
    Setup.CreateShortcut()