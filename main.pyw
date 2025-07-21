from common.utils import Log, Security
from minibar import gui as inf
from common.sound import Master as cm
import customtkinter as ctk

class Auth():

    @staticmethod
    def CheckPassword(account_name: str, used_password: str):
        return Security.IsPasswordRight(used_password, account_name)


class App(ctk.CTk):

    def __init__(self, lang="ru"):
        super().__init__()
        ctk.set_default_color_theme("green")
        self.lang = lang

    def change_lang(self):
        if self.lang == "uz": self.lang = "ru"
        else: self.lang = "uz"

        self.language_button.configure(text=self.lang.upper())

    def entrance(self, account_type="user", password="-"):
        result = Auth.CheckPassword(account_type.lower(), password)
        if result:
            self.destroy()
            cm.Play("start")
            app = inf.App(permission=account_type.lower(), locale=self.lang)
            app.mainloop()

        else:
            cm.Play("error", number=1)
            self.label.configure(text="Неверный пароль!", text_color="red", font=("Arial", 18))


    def on_select(self, account_type):
        self.label.configure(text=f"Выбран аккаунт: {account_type}")

        self.user_button.pack_forget()
        self.manager_button.pack_forget()
        self.select_button.pack_forget()

        if account_type=="manager":
            self.password_entry = ctk.CTkEntry(self, show="*", placeholder_text="Пароль")
            self.password_entry.pack()

        self.entrance_button = ctk.CTkButton(self, text="Войти", command=lambda: self.entrance(account_type, self.password_entry.get() if account_type=="manager" else "-"))
        self.entrance_button.pack()

    def show_options(self):
        self.window_height +=65
        x = (self.screen_width // 2) - (self.window_width // 2)
        y = (self.screen_height // 2) - (self.window_height // 2)
        self.geometry(f"{self.window_width}x{self.window_height}+{x}+{y}")
        self.user_button.pack(pady=5)
        self.manager_button.pack(pady=5)

    def setup_ui(self):
        self.window_width = 300
        self.window_height = 100

        self.screen_width = self.winfo_screenwidth()
        self.screen_height = self.winfo_screenheight()

        x = (self.screen_width // 2) - (self.window_width // 2)
        y = (self.screen_height // 2) - (self.window_height // 2)

        self.configure(background="green")
        self.geometry(f"{self.window_width}x{self.window_height}+{x}+{y}")
        self.title("Выбор аккаунта")

        self.label = ctk.CTkLabel(self, text="Выберите аккаунт")
        self.label.pack(pady=10)

        self.select_button = ctk.CTkButton(self, text="Выбрать аккаунт", command=self.show_options)
        self.select_button.pack(pady=10)

        self.user_button = ctk.CTkButton(self, text="Пользователь", command=lambda: self.on_select("user"), width=20, height=20, fg_color="blue2", hover_color="blue")
        self.manager_button = ctk.CTkButton(self, text="Менеджер", command=lambda: self.on_select("manager"), width=20, height=20, fg_color="blue2", hover_color="blue")

        self.language_button = ctk.CTkButton(self, text="RU", command=self.change_lang, width=30, height=30, font=("MS Gothic", 15, "bold"), hover_color="gray")
        self.language_button.place(x=270, y=0)



if __name__ == "__main__":
    import updater
    updater.update_from_manifest()
    app = App()
    app.setup_ui()
    app.mainloop()