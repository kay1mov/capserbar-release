import customtkinter as ctk
from tkinter import ttk, messagebox
from minibar.logic import *
from tkcalendar import DateEntry
from common.translate import Translator

class App(ctk.CTk):
    def __init__(self, permission="user", locale="ru"):
        super().__init__()
        self.locale = locale
        self.permission = permission

        _ = Translator(locale=locale    )
        self.title(f"Bar Manager - " + f"({_('Администратор')})" if permission == "manager" else "")
        self.geometry("1500x700")

        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme(THEMES_DIR / "breeze.json" if permission == "manager" else "blue")
        self.setup_initial_data()

        # --- Основной layout ---
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- Навигационная панель ---
        self.nav_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.nav_frame.grid(row=0, column=0, sticky="nswe")
        self.nav_frame.grid_rowconfigure(4, weight=1)

        self.nav_label = ctk.CTkLabel(self.nav_frame, text=_("Управление"), font=ctk.CTkFont(size=20, weight="bold"))
        self.nav_label.grid(row=0, column=0, padx=20, pady=20)

        self.btn_sales = ctk.CTkButton(self.nav_frame, text=_("Продажа"),
                                       command=lambda: self.select_frame("sales"))
        self.btn_sales.grid(row=1, column=0, padx=20, pady=10, sticky="ew")

        self.btn_storage = ctk.CTkButton(self.nav_frame, text=_("Склад"), command=lambda: self.select_frame("storage"))
        self.btn_storage.grid(row=2, column=0, padx=20, pady=10, sticky="ew")

        self.btn_history = ctk.CTkButton(self.nav_frame, text=_("История"), command=lambda: self.select_frame("history"))
        self.btn_history.grid(row=3, column=0, padx=20, pady=10, sticky="ew")

        # --- Создание фреймов для каждого раздела ---
        self.sales_frame = ctk.CTkFrame(self)
        self.storage_frame = ctk.CTkFrame(self)
        self.history_frame = ctk.CTkFrame(self)

        self.create_sales_widgets()
        self.create_storage_widgets()
        self.create_history_widgets()

        # --- Изначально выбранный фрейм ---
        self.select_frame("sales")

    def setup_initial_data(self):
        global _
        storage_path = DATA_DIR / "storage.json"
        _ = Translator(self.locale)
        if not storage_path.exists() or not IO.LoadJSON(storage_path):
            # Создаем несколько товаров для примера
            try:
                Storage.NewProduct("Cola 1.5", 15000, 1)
                Storage.NewProduct("Вода 0.5", 3000, 1)
            except Exception:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                Log.FATAL((exc_type, exc_value, exc_traceback))

    def select_frame(self, name):
        # Сначала скрываем все фреймы
        self.sales_frame.grid_forget()
        self.storage_frame.grid_forget()
        self.history_frame.grid_forget()

        # Показываем выбранный
        if name == "sales":
            self.sales_frame.grid(row=0, column=1, sticky="nswe", padx=20, pady=20)
            self.refresh_all_sales_data()
        elif name == "storage":
            self.storage_frame.grid(row=0, column=1, sticky="nswe", padx=20, pady=20)
            self.refresh_storage_table()
        elif name == "history":
            self.history_frame.grid(row=0, column=1, sticky="nswe", padx=20, pady=20)
            self.refresh_history_table()

    def create_sales_widgets(self):
        """Создает все виджеты для вкладки продаж."""
        self.sales_frame.grid_columnconfigure(0, weight=3)
        self.sales_frame.grid_columnconfigure(1, weight=1)
        self.sales_frame.grid_rowconfigure(0, weight=1)

        # --- Левая часть - Поиск и витрина товаров ---

        # Контейнер для поиска и списка товаров
        left_frame = ctk.CTkFrame(self.sales_frame, fg_color="transparent")
        left_frame.grid(row=0, column=0, padx=(0, 10), pady=10, sticky="nswe")
        left_frame.grid_rowconfigure(1, weight=1)
        left_frame.grid_columnconfigure(0, weight=1)

        # Поле и кнопка поиска
        search_container = ctk.CTkFrame(left_frame)
        search_container.grid(row=0, column=0, padx=0, pady=(0, 10), sticky="ew")
        search_container.grid_columnconfigure(0, weight=1)

        self.search_var = ctk.StringVar()
        self.search_var.trace_add("write", lambda *args: self.search_products())
        self.search_entry = ctk.CTkEntry(search_container, textvariable=self.search_var,
                                         placeholder_text=_("Поиск товара")+"...")
        self.search_entry.grid(row=0, column=0, padx=(0, 10), pady=5, sticky="ew")

        self.products_scroll_frame = ctk.CTkScrollableFrame(left_frame, label_text=_("Товары"))
        self.products_scroll_frame.grid(row=1, column=0, sticky="nswe")
        self.products_scroll_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        # Общая сумма всех товаров на складе
        self.total_products_sum_label = ctk.CTkLabel(
            left_frame,
            text="",  # Текст будет установлен в update_total_products_sum
            font=ctk.CTkFont(size=14, weight="normal")
        )
        self.total_products_sum_label.grid(row=2, column=0, padx=10, pady=5, sticky="w")

        # --- Правая часть - Корзина ---
        self.cart_frame = ctk.CTkFrame(self.sales_frame)
        self.cart_frame.grid(row=0, column=1, padx=(10, 0), pady=10, sticky="nswe")
        self.cart_frame.grid_rowconfigure(1, weight=1)
        self.cart_frame.grid_columnconfigure((0, 1), weight=1)

        self.cart_label = ctk.CTkLabel(self.cart_frame, text=_("Корзина"), font=ctk.CTkFont(size=16, weight="bold"))
        self.cart_label.grid(row=0, column=0, columnspan=2, padx=10, pady=10)

        self.cart_text = ctk.CTkTextbox(self.cart_frame, state="disabled", font=("Consolas", 12))
        self.cart_text.grid(row=1, column=0, columnspan=2, padx=10, pady=5, sticky="nswe")

        self.total_label = ctk.CTkLabel(self.cart_frame, text=f"{_('Итого')}: 0.00 {_('сум')}.",
                                        font=ctk.CTkFont(size=18, weight="bold"))
        self.total_label.grid(row=2, column=0, columnspan=2, padx=10, pady=10)

        self.btn_pay = ctk.CTkButton(self.cart_frame, text=_("Оплатить"), command=self.process_payment)
        self.btn_pay.grid(row=3, column=0, padx=10, pady=10, sticky="ew")

        self.btn_clear_cart = ctk.CTkButton(self.cart_frame, text=_("Очистить"), fg_color="gray",
                                            command=self.clear_cart)
        self.btn_clear_cart.grid(row=3, column=1, padx=10, pady=10, sticky="ew")

        self.cart = {}  # {product_name: count}

        # Первоначальная загрузка и отображение
        self.refresh_all_sales_data()

    def search_products(self):
        """Фильтрует и отображает товары на основе текста в поле поиска."""
        search_text = self.search_var.get().strip().lower()
        all_products = Storage.LoadProducts()

        if not search_text:
            products_to_show = all_products
        else:
            products_to_show = {
                name: data for name, data in all_products.items()
                if search_text in name.lower()
            }

        self._display_products(products_to_show)

    def _display_products(self, products_to_display: dict):
        """
        Внутренний метод для очистки и отображения переданного списка товаров.
        Это предотвращает дублирование кода.
        """
        # Очистить старые виджеты
        for widget in self.products_scroll_frame.winfo_children():
            widget.destroy()

        # Отобразить новые товары в виде сетки
        row, col = 0, 0
        for name, data in products_to_display.items():
            btn_text = f"{name}\n{data['price']} {_('сум')}.\n{_('Остаток')}: {data['count']}"
            btn = ctk.CTkButton(
                self.products_scroll_frame,
                text=btn_text,
                height=120,
                command=lambda n=name: self.add_to_cart(n)
            )
            # Если товара нет в наличии, делаем кнопку неактивной
            if data['count'] <= 0:
                btn.configure(state="disabled", fg_color="gray")

            btn.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
            col += 1
            if col > 3:  # 4 кнопки в ряду
                col = 0
                row += 1

    def update_total_products_sum(self):
        """Обновляет метку с общей стоимостью всех товаров на складе."""
        total = Storage.GetTotalProductsSum()  # Предполагается, что эта функция считает price * count для всех товаров
        self.total_products_sum_label.configure(text=f"{_('Общая стоимость товаров')}: {total:,.2f} {_('сум')}")

    def refresh_all_sales_data(self):
        """Обновляет список товаров и общую сумму на складе."""
        all_products = Storage.LoadProducts()
        self._display_products(all_products)
        self.update_total_products_sum()
        # Очищаем поиск, чтобы не смущать пользователя
        self.search_var.set("")

    def update_cart_display(self):
        self.cart_text.configure(state="normal")
        self.cart_text.delete("1.0", "end")

        total_price = 0
        products = Storage.LoadProducts()

        if not self.cart:
            self.cart_text.insert("end", _("Корзина пуста"))
        else:
            header = f"{_('Название'):<25}{_('Кол-во'):>7}{_('Цена'):>10}{_('Сумма'):>12}\n"
            separator = "-" * 54 + "\n"
            self.cart_text.insert("end", header)
            self.cart_text.insert("end", separator)

            for name, count in self.cart.items():
                price = products[name]['price']
                line_total = price * count
                total_price += line_total
                line = f"{name:<25}{count:>7}{price:>10.2f}{line_total:>12.2f}\n"
                self.cart_text.insert("end", line)

        self.total_label.configure(text=f"{_('Итого')}: {total_price:.2f} {_('сум')}.")
        self.cart_text.configure(state="disabled")

    def process_payment(self):
        if not self.cart:
            messagebox.showinfo(_("Информация"), _("Корзина пуста."))
            return

        try:
            for name, count in self.cart.items():
                Sales.Sale(name, count)
            messagebox.showinfo(_("Успех"), _("Продажа успешно оформлена!"))
            self.clear_cart()
            self.refresh_all_sales_data()
            self.update_total_products_sum()
        except (ValueError, NameError) as e:
            messagebox.showerror(_("Ошибка продажи"), str(e))

    def clear_cart(self):
        self.cart = {}
        self.update_cart_display()

    def add_to_cart(self, product_name):
        products = Storage.LoadProducts()
        stock = products[product_name]['count']

        in_cart_count = self.cart.get(product_name, 0)

        if in_cart_count >= stock:
            messagebox.showwarning("Внимание", f"Недостаточно товара '{product_name}' на складе.")
            return

        self.cart[product_name] = self.cart.get(product_name, 0) + 1
        self.update_cart_display()

    # --- РАЗДЕЛ СКЛАД ---
    def create_storage_widgets(self):
        self.storage_frame.grid_rowconfigure(0, weight=1)
        self.storage_frame.grid_columnconfigure(0, weight=1)

        # Таблица товаров
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", background="#2b2b2b", foreground="white", fieldbackground="#2b2b2b", borderwidth=0)
        style.map('Treeview', background=[('selected', '#2a3a50')])
        style.configure("Treeview.Heading", background="#565b5e", foreground="white", font=('Calibri', 12, 'bold'))

        self.storage_table = ttk.Treeview(self.storage_frame, columns=("name", "price", "count"), show="headings")
        self.storage_table.heading("name", text=_("Название"))
        self.storage_table.heading("price", text=_("Цена (сум.)"))
        self.storage_table.heading("count", text=_("Количество (шт.)"))
        self.storage_table.grid(row=0, column=0, columnspan=3, sticky="nswe", padx=10, pady=10)

        # Кнопки управления

        if self.permission == "manager":
            self.btn_add = ctk.CTkButton(self.storage_frame, text=_("Добавить товар"), command=self.add_product_dialog)
            self.btn_add.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

            self.btn_edit = ctk.CTkButton(self.storage_frame, text=_("Редактировать"), command=self.edit_product_dialog)
            self.btn_edit.grid(row=1, column=1, padx=10, pady=10, sticky="ew")

            self.btn_delete = ctk.CTkButton(self.storage_frame, text=_("Удалить"), fg_color="red", hover_color="darkred",
                                            command=self.delete_product)
            self.btn_delete.grid(row=1, column=2, padx=10, pady=10, sticky="ew")

    def refresh_storage_table(self):
        for i in self.storage_table.get_children():
            self.storage_table.delete(i)

        products = Storage.LoadProducts()
        for name, data in products.items():
            self.storage_table.insert("", "end", values=(name, data['price'], data['count']))

    def add_product_dialog(self):
        dialog = ctk.CTkInputDialog(text=_("Введите название")+":", title=_("Добавить товар"))
        name = dialog.get_input()
        if not name: return

        dialog = ctk.CTkInputDialog(text=_("Введите цену (число)")+":", title=_("Добавить товар"))
        price_str = dialog.get_input()
        if not price_str: return

        dialog = ctk.CTkInputDialog(text=_("Введите количество (целое число)")+":", title=_("Добавить товар"))
        count_str = dialog.get_input()
        if not count_str: return

        try:
            price = float(price_str.replace(",", "."))
            count = int(count_str)
            Storage.NewProduct(name, price, count)
            messagebox.showinfo(_("Успех"), f"{_('Товар')} '{name}' {_('успешно добавлен')}.")
            self.refresh_storage_table()
        except (ValueError, TypeError) as e:
            messagebox.showerror(_("Ошибка"), f"{_('Некорректные данные')}: {e}")

    def edit_product_dialog(self):
        print(self.permission)
        if self.permission != "manager": return
        selected_item = self.storage_table.focus()
        if not selected_item:
            messagebox.showwarning(_("Внимание"), _("Выберите товар для редактирования."))
            return

        item_values = self.storage_table.item(selected_item)['values']
        name, old_price, old_count = item_values[0], item_values[1], item_values[2]

        # Редактирование цены
        dialog = ctk.CTkInputDialog(text=f"{_('Новая цена для')} '{name}' ({_('текущая')}): {old_price}):", title=_("Редактировать цену"))
        new_price_str = dialog.get_input()
        if new_price_str:
            try:
                new_price = float(new_price_str.replace(",", "."))
                Storage.Change(name, "price", new_price)
            except ValueError:
                messagebox.showerror(_("Ошибка"), _("Цена должна быть числом."))
                return

        # Редактирование количества
        dialog = ctk.CTkInputDialog(text=f"{_('Новое количество для')} '{name}' ({_('текущее')}: {old_count}):",
                                    title=_("Редактировать количество"))
        new_count_str = dialog.get_input()
        if new_count_str:
            try:
                new_count = int(new_count_str)
                Storage.Change(name, "count", new_count)
            except ValueError:
                messagebox.showerror(_("Ошибка"), _("Количество должно быть целым числом."))
                return

        messagebox.showinfo(_("Успех"), _("Данные товара обновлены."))
        self.refresh_all_views()

    def delete_product(self):
        selected_item = self.storage_table.focus()
        if not selected_item:
            messagebox.showwarning(_("Внимание"), _("Выберите товар для удаления."))
            return

        name = self.storage_table.item(selected_item)['values'][0]
        if messagebox.askyesno(_("Подтверждение"),
                               f"{_('Вы уверены, что хотите удалить товар')} '{name}'? {_('Это действие необратимо')}."):
            try:
                Storage.Delete(name)
                messagebox.showinfo(_("Успех"), _("Товар") + " " + name +  _("удален") +".")
                self.refresh_all_views()
            except Exception as e:
                messagebox.showerror(_("Ошибка"), str(e))

    def create_history_widgets(self):
        # --- НОВЫЙ КОД: Панель управления с фильтрами и информацией ---
        top_frame = ctk.CTkFrame(self.history_frame)
        top_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=(10, 0))
        top_frame.grid_columnconfigure(1, weight=1)

        # Лейбл для итоговой выручки за день
        summary_font = ctk.CTkFont(size=20, weight="bold")
        self.summary_label = ctk.CTkLabel(top_frame, text=f"{_('Выручка за день')}: 0.00 {_('сум')}", font=summary_font, anchor="w")
        self.summary_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        # Фильтр по дате
        filter_frame = ctk.CTkFrame(top_frame)
        filter_frame.grid(row=0, column=1, padx=10, pady=10, sticky="e")

        ctk.CTkLabel(filter_frame, text=_("Показать продажи за")+":").pack(side="left", padx=(0, 5))

        # Виджет выбора даты
        self.date_entry = DateEntry(filter_frame, width=12, background='darkblue',
                                    foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
        self.date_entry.pack(side="left", padx=5)

        # Кнопки для применения фильтра
        self.btn_apply_filter = ctk.CTkButton(filter_frame, text=_("Показать"), width=100,
                                              command=self.apply_history_filter)
        self.btn_apply_filter.pack(side="left", padx=5)

        self.btn_show_all = ctk.CTkButton(filter_frame, text=_("Показать все"), width=120,
                                          command=self.refresh_history_table)
        self.btn_show_all.pack(side="left", padx=5)
        # --- Конец нового кода ---

        # Конфигурация основной сетки
        self.history_frame.grid_rowconfigure(1, weight=1)  # ИЗМЕНЕНО: теперь таблица во второй строке
        self.history_frame.grid_columnconfigure(0, weight=1)

        # Таблица истории (без изменений, только позиция в grid)
        self.history_table = ttk.Treeview(self.history_frame, columns=("id", "date", "name", "count", "price", "total"),
                                          show="headings")
        self.history_table.heading("id", text=_("ID Продажи")),
        self.history_table.heading("date", text=_("Дата и время")),
        self.history_table.heading("name", text=_("Название")),
        self.history_table.heading("count", text=_("Кол-во")),
        self.history_table.heading("price", text=_("Цена за шт.")),
        self.history_table.heading("total", text=_("Итого"))

        self.history_table.column("id", width=250, anchor='w')
        self.history_table.column("date", width=150, anchor='w')

        # ИЗМЕНЕНО: позиция таблицы
        self.history_table.grid(row=1, column=0, columnspan=2, sticky="nswe", padx=10, pady=10)

        # Кнопка возврата (позиция изменена)
        self.btn_refund = ctk.CTkButton(self.history_frame, text=_("Оформить возврат"), command=self.refund_sale)
        self.btn_refund.grid(row=2, column=0, columnspan=2, padx=10, pady=10)  # ИЗМЕНЕНО: позиция

        # Поле с подробной информацией (позиция изменена)
        self.details_label = ctk.CTkLabel(self.history_frame, text=_("Подробности выбранной продажи")+":", anchor="w")
        self.details_label.grid(row=3, column=0, columnspan=2, padx=10, pady=(10, 0), sticky="w")  # ИЗМЕНЕНО: позиция

        self.details_text = ctk.CTkTextbox(self.history_frame, height=100, state="disabled")
        self.details_text.grid(row=4, column=0, columnspan=2, sticky="ew", padx=10, pady=10)  # ИЗМЕНЕНО: позиция

        self.history_table.bind("<<TreeviewSelect>>", self.show_sale_details)

    # НОВЫЙ КОД: Обработчик для кнопки "Показать"
    def apply_history_filter(self):
        """ Получает дату из DateEntry и вызывает обновление таблицы с фильтром """
        selected_date = self.date_entry.get_date()
        self.refresh_history_table(filter_date=selected_date)

    # ИЗМЕНЕНО: Функция обновления таблицы теперь принимает дату для фильтрации
    def refresh_history_table(self, filter_date=None):
        """
        Обновляет таблицу истории.
        Если filter_date задан, показывает продажи только за этот день.
        """
        # Очищаем таблицу и детали
        for i in self.history_table.get_children():
            self.history_table.delete(i)

        self.details_text.configure(state="normal")
        self.details_text.delete("1.0", "end")
        self.details_text.configure(state="disabled")

        sales = IO.LoadJSON(DATA_DIR / "sales.json")
        sorted_sales = sorted(sales.items(), key=lambda item: item[1]['date'], reverse=True)

        total_revenue_for_period = 0.0

        for sale_id, data in sorted_sales:
            dt_obj = datetime.datetime.fromisoformat(data['date'])

            # Логика фильтрации
            if filter_date and dt_obj.date() != filter_date:
                continue  # Пропускаем запись, если дата не совпадает

            # Если запись подходит, добавляем ее в таблицу
            formatted_date = dt_obj.strftime("%Y-%m-%d %H:%M:%S")
            total = data.get('total_price', data['price'] * data['count'])

            total_revenue_for_period += total

            self.history_table.insert("", "end", values=(sale_id, formatted_date, data['name'], data['count'],
                                                         f"{data['price']:.2f}", f"{total:.2f}"))

        # Обновляем лейбл с выручкой
        if filter_date:
            date_str = filter_date.strftime('%d.%m.%Y')
            self.summary_label.configure(text=f"{_('Выручка за')} {date_str}: {total_revenue_for_period:,.2f}{_('сум')}")
        else:
            self.summary_label.configure(text=f"{_('Общая выручка')}: {total_revenue_for_period:,.2f} {_('сум')}")

    def show_sale_details(self, event=None):
        selected_item = self.history_table.focus()
        if not selected_item:
            # Очищаем поле деталей, если выбор снят
            self.details_text.configure(state="normal")
            self.details_text.delete("1.0", "end")
            self.details_text.configure(state="disabled")
            return

        values = self.history_table.item(selected_item)['values']
        sale_id, date, name, count, price, total = values

        details = (
            f"{_('ID Продажи')}: {sale_id}\n"
            f"{_('Дата')}: {date}\n"
            f"{_('Товар')}: {name}\n"
            f"{_('Количество')}: {count} {_('шт')}.\n"
            f"{_('Цена за единицу')}: {price} {_('сум')}\n"  # Убрал точку из "сум."
            f"{_('Общая сумма')}: {total} {_('сум')}"
        )

        self.details_text.configure(state="normal")
        self.details_text.delete("1.0", "end")
        self.details_text.insert("1.0", details)
        self.details_text.configure(state="disabled")

    def refund_sale(self):
        selected_item = self.history_table.focus()
        if not selected_item:
            messagebox.showwarning(_("Внимание"), _("Выберите продажу для возврата."))
            return

        sale_id = self.history_table.item(selected_item)['values'][0]
        name = self.history_table.item(selected_item)['values'][2]

        if messagebox.askyesno(_("Подтверждение"),
                               f"{_('Вы уверены, что хотите оформить возврат для')} '{name}' (ID: {sale_id})? {_('Товар вернется на склад')}."):
            try:
                Sales.Refund(sale_id)
                messagebox.showinfo(_("Успех"), _("Возврат успешно оформлен."))
                # self.refresh_all_views() # Предполагается, что эта функция обновляет все, включая историю
                # Если refresh_all_views не вызывает refresh_history_table, то нужно вызвать ее явно
                self.refresh_history_table()  # Обновляем с показом всех продаж после возврата
            except Exception as e:
                messagebox.showerror(_("Ошибка"), str(e))
    # --- Утилиты ---
    def refresh_all_views(self):
        """Обновляет данные на всех вкладках."""
        self.refresh_all_sales_data()
        self.refresh_storage_table()
        self.refresh_history_table()


