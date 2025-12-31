import tkinter as tk
from tkinter import messagebox, ttk
import requests

BASE_URL = "http://127.0.0.1:8000"

class MainApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Биржа Просмотров")
        self.root.geometry("600x700")
        self.current_user = None
        
        # Сразу скрываем главное окно и показываем окно входа
        self.root.withdraw()
        self.show_login_window()

    # --- ОКНО ВХОДА ---
    def show_login_window(self):
        self.login_win = tk.Toplevel()
        self.login_win.title("Авторизация")
        self.login_win.geometry("300x250")
        self.login_win.protocol("WM_DELETE_WINDOW", self.root.quit)

        tk.Label(self.login_win, text="Логин:").pack(pady=5)
        self.ent_login = tk.Entry(self.login_win)
        self.ent_login.pack()

        tk.Label(self.login_win, text="Пароль:").pack(pady=5)
        self.ent_pass = tk.Entry(self.login_win, show="*")
        self.ent_pass.pack()

        tk.Button(self.login_win, text="Войти", command=self.process_login, bg="#d1e7ff").pack(pady=10)
        tk.Button(self.login_win, text="Нет аккаунта? Регистрация", command=self.show_register_window, bd=0, fg="blue").pack()

    def process_login(self):
        u = self.ent_login.get()
        p = self.ent_pass.get()
        try:
            r = requests.post(f"{BASE_URL}/login", json={"username": u, "password": p})
            res = r.json()
            if res.get("status") == "success":
                self.current_user = res["user"]
                self.login_win.destroy()
                self.setup_main_ui() # Строим основной интерфейс
                self.root.deiconify() # Показываем главное окно
            else:
                messagebox.showerror("Ошибка", res.get("message"))
        except:
            messagebox.showerror("Ошибка", "Сервер недоступен")

    # --- ОКНО РЕГИСТРАЦИИ ---
    def show_register_window(self):
        reg_win = tk.Toplevel(self.login_win)
        reg_win.title("Регистрация")
        reg_win.geometry("300x300")
        reg_win.grab_set()

        tk.Label(reg_win, text="Придумайте логин:").pack(pady=2)
        ent_u = tk.Entry(reg_win); ent_u.pack()

        tk.Label(reg_win, text="Ваш Email:").pack(pady=2)
        ent_e = tk.Entry(reg_win); ent_e.pack()

        tk.Label(reg_win, text="Придумайте пароль:").pack(pady=2)
        ent_p = tk.Entry(reg_win, show="*"); ent_p.pack()

        def submit():
            u = ent_u.get().strip()
            e = ent_e.get().strip()
            p = ent_p.get().strip()
            
            if not u or not e or not p:
                messagebox.showwarning("Внимание", "Заполните все поля!")
                return

            data = {"username": u, "email": e, "password": p}
            try:
                r = requests.post(f"{BASE_URL}/register", json=data)
                
                if r.status_code == 200:
                    res = r.json()
                    messagebox.showinfo("Успех", "Регистрация завершена!")
                    reg_win.destroy()
                
                elif r.status_code == 422:
                    # Это ошибка валидации (неверный email)
                    res = r.json()
                    # Проверяем, есть ли в ошибке упоминание email
                    detail = res.get("detail", [])
                    if any("email" in str(d.get("loc")) for d in detail):
                        messagebox.showerror("Ошибка", "Неверный формат почты! Пример: user@mail.com")
                    else:
                        messagebox.showerror("Ошибка", "Проверьте правильность введенных данных")
                
                elif r.status_code == 500:
                    messagebox.showerror("Ошибка", "Ошибка на стороне сервера (проблема с bcrypt)")
                
                else:
                    messagebox.showerror("Ошибка", f"Код ошибки: {r.status_code}")

            except Exception as ex:
                messagebox.showerror("Ошибка связи", f"Не удалось достучаться до сервера: {ex}")

        tk.Button(reg_win, text="Зарегистрироваться", command=submit, bg="#e1ebe1").pack(pady=15)

    # --- ОСНОВНОЙ ИНТЕРФЕЙС ---
    def setup_main_ui(self):
        # Очищаем root если там что-то было
        for widget in self.root.winfo_children():
            widget.destroy()

        # Панель игрока
        top = tk.Frame(self.root, pady=10)
        top.pack(fill="x", padx=10)
        
        self.lbl_user = tk.Label(top, text=f"Пользователь: {self.current_user['username']}", font=("Arial", 10, "bold"))
        self.lbl_user.pack(side="left")
        
        self.lbl_balance = tk.Label(top, text=f"Баланс: {self.current_user['points']} 🪙", fg="green")
        self.lbl_balance.pack(side="right")

        # Кнопка Выхода
        tk.Button(self.root, text="Выйти из аккаунта", command=self.logout).pack(pady=5)

        # --- 3. СЕКЦИЯ СОЗДАНИЯ ЗАКАЗА ---
        self.order_frame = tk.LabelFrame(root, text="Разместить новый заказ", padx=10, pady=10)
        self.order_frame.pack(fill="x", padx=10, pady=5)

        tk.Label(self.order_frame, text="Название:").grid(row=0, column=0, sticky="w")
        self.order_title = tk.Entry(self.order_frame)
        self.order_title.grid(row=0, column=1, sticky="we", padx=5, pady=2)

        tk.Label(self.order_frame, text="URL ссылки:").grid(row=1, column=0, sticky="w")
        self.order_url = tk.Entry(self.order_frame)
        self.order_url.grid(row=1, column=1, sticky="we", padx=5, pady=2)
        
        self.order_frame.columnconfigure(1, weight=1)

        self.btn_buy_trigger = tk.Button(
            self.order_frame, 
            text="Купить просмотры (Рассчитать стоимость)", 
            command=self.open_buy_modal, 
            # state="disabled",
            bg="#d1e7ff"
        )
        self.btn_buy_trigger.grid(row=2, columnspan=2, pady=10)

        # --- 4. ТАБЛИЦА ДОСТУПНЫХ ЗАДАЧ (ДЛЯ ЗАРАБОТКА) ---
        self.task_frame = tk.LabelFrame(root, text="Доступные задачи (Заработок +5)", padx=10, pady=10)
        self.task_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.task_list = ttk.Treeview(self.task_frame, columns=("ID", "Title"), show="headings", height=5)
        self.task_list.heading("ID", text="ID")
        self.task_list.heading("Title", text="Заголовок задания")
        self.task_list.column("ID", width=50)
        self.task_list.pack(fill="both", expand=True)

        btn_box = tk.Frame(self.task_frame)
        btn_box.pack(pady=5)
        
        self.refresh_btn = tk.Button(btn_box, text="Обновить список", command=self.load_tasks)
        self.refresh_btn.pack(side="left", padx=5)
        
        self.complete_btn = tk.Button(btn_box, text="ВЫПОЛНИТЬ ВЫБРАННУЮ", command=self.complete_task, bg="#fff3cd")
        self.complete_btn.pack(side="left", padx=5)

        # --- 5. ТАБЛИЦА ВСЕХ ЗАКАЗОВ В БД (ОБЩИЙ МОНИТОРИНГ) ---
        self.db_frame = tk.LabelFrame(root, text="Все заказы в системе (Мониторинг)", padx=10, pady=10)
        self.db_frame.pack(fill="x", padx=10, pady=5)
        
        self.db_tree = ttk.Treeview(self.db_frame, columns=("ID", "Title", "URL"), show="headings", height=5)
        self.db_tree.heading("ID", text="ID")
        self.db_tree.heading("Title", text="Название")
        self.db_tree.heading("URL", text="Ссылка")
        self.db_tree.column("ID", width=40)
        self.db_tree.pack(fill="both", expand=True)

    # --- ЛОГИКА ---

    def login(self):
        user_id = self.user_id_entry.get()
        try:
            r = requests.get(f"{BASE_URL}/users/{user_id}")
            if r.status_code == 200:
                self.current_user = r.json()
                self.update_ui_state("logged_in")
                self.load_tasks()
                self.load_db_orders()
            else:
                messagebox.showerror("Ошибка", "Пользователь не найден")
        except:
            messagebox.showerror("Ошибка", "Сервер не отвечает")

    def logout(self):
        self.current_user = None
        self.update_ui_state("logged_out")
        self.task_list.delete(*self.task_list.get_children())
        self.db_tree.delete(*self.db_tree.get_children())

    def update_ui_state(self, state):
        if state == "logged_in":
            self.status_label.config(text=f"Юзер: {self.current_user['username']}", fg="green")
            self.balance_label.config(text=f"Баллы: {self.current_user['points']}")
            self.login_btn.config(state="disabled")
            self.logout_btn.config(state="normal")
            self.btn_buy_trigger.config(state="normal")
            self.refresh_btn.config(state="normal")
            self.complete_btn.config(state="normal")
        else:
            self.status_label.config(text="Статус: Не авторизован", fg="red")
            self.balance_label.config(text="Баллы: 0")
            self.login_btn.config(state="normal")
            self.logout_btn.config(state="disabled")
            self.btn_buy_trigger.config(state="disabled")
            self.refresh_btn.config(state="disabled")
            self.complete_btn.config(state="disabled")

    # --- МОДАЛЬНОЕ ОКНО С КАЛЬКУЛЯТОРОМ ---
    def open_buy_modal(self):
        title = self.order_title.get()
        url = self.order_url.get()
        if not title or not url:
            messagebox.showwarning("Внимание", "Заполните Название и URL сначала!")
            return

        modal = tk.Toplevel(self.root)
        modal.title("Оформление заказа")
        modal.geometry("350x250")
        modal.grab_set()

        tk.Label(modal, text="Сколько просмотров нужно?", font=("Arial", 10)).pack(pady=10)
        
        ent_count = tk.Entry(modal, font=("Arial", 12), justify='center')
        ent_count.pack(pady=5)
        ent_count.insert(0, "10")

        lbl_price = tk.Label(modal, text="Итоговая стоимость: 50 баллов", font=("Arial", 10, "bold"), fg="blue")
        lbl_price.pack(pady=10)

        def recalc(event=None):
            try:
                val = ent_count.get()
                count = int(val) if val else 0
                lbl_price.config(text=f"Итоговая стоимость: {count * 5} баллов", fg="blue")
            except:
                lbl_price.config(text="Введите число!", fg="red")

        ent_count.bind("<KeyRelease>", recalc)

        def confirm_purchase():
            try:
                count = int(ent_count.get())
                self.send_order_to_server(title, url, count, modal)
            except:
                messagebox.showerror("Ошибка", "Некорректное число")

        tk.Button(modal, text="Оплатить и запустить", command=confirm_purchase, bg="#d1e7ff", padx=10).pack(pady=10)

    def send_order_to_server(self, title, url, count, modal_window):
        payload = {
            "user_id": self.current_user["id"],
            "title": title,
            "target_url": url,
            "views_count": count
        }
        try:
            r = requests.post(f"{BASE_URL}/orders/create", json=payload)
            res = r.json()
            if res.get("status") == "success":
                messagebox.showinfo("Успех", res["message"])
                modal_window.destroy()
                self.login() # Обновить баллы
                self.load_db_orders()
            else:
                messagebox.showerror("Ошибка", res.get("message"))
        except:
            messagebox.showerror("Ошибка", "Нет связи с сервером")

    # --- ЗАГРУЗКА ДАННЫХ ---
    def load_tasks(self):
        self.task_list.delete(*self.task_list.get_children())
        try:
            r = requests.get(f"{BASE_URL}/tasks/available/{self.current_user['id']}")
            for t in r.json():
                self.task_list.insert("", "end", values=(t["id"], t["title"]))
        except: pass

    def load_db_orders(self):
        self.db_tree.delete(*self.db_tree.get_children())
        try:
            r = requests.get(f"{BASE_URL}/orders/all")
            for o in r.json():
                self.db_tree.insert("", "end", values=(o["id"], o["title"], o["target_url"]))
        except: pass

    def complete_task(self):
        sel = self.task_list.selection()
        if not sel: return
        t_id = self.task_list.item(sel[0])["values"][0]
        
        try:
            r = requests.post(f"{BASE_URL}/tasks/complete", json={"user_id": self.current_user["id"], "order_id": t_id})
            res = r.json()
            if res.get("status") == "success":
                messagebox.showinfo("Готово", "+5 баллов!")
                self.login()
            else:
                messagebox.showerror("Упс", res.get("message"))
        except: pass

    def logout(self):
        self.current_user = None
        self.root.withdraw()
        self.show_login_window()

if __name__ == "__main__":
    root = tk.Tk()
    app = MainApp(root)
    root.mainloop()