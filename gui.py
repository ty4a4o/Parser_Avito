import tkinter as tk
from tkinter import messagebox, ttk
import requests
import threading
import act  # Скрипт твоего товарища

BASE_URL = "http://127.0.0.1:8000"

class MainApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Биржа Просмотров + Avito Bot")
        self.root.geometry("700x800")
        self.current_user = None

        # Скрываем главное окно при старте, показываем логин
        self.root.withdraw()
        self.show_login_window()

    # ---------------------------------------------------------
    # 1. СЕКЦИЯ АВТОРИЗАЦИИ И РЕГИСТРАЦИИ (Твой старый код)
    # ---------------------------------------------------------
    def show_login_window(self):
        self.login_win = tk.Toplevel()
        self.login_win.title("Вход в систему")
        self.login_win.geometry("300x250")
        self.login_win.protocol("WM_DELETE_WINDOW", self.root.quit)

        tk.Label(self.login_win, text="Логин:").pack(pady=5)
        self.ent_login = tk.Entry(self.login_win)
        self.ent_login.pack()

        tk.Label(self.login_win, text="Пароль:").pack(pady=5)
        self.ent_pass = tk.Entry(self.login_win, show="*")
        self.ent_pass.pack()

        tk.Button(self.login_win, text="Войти", command=self.process_login, bg="#d1e7ff", width=20).pack(pady=10)
        tk.Button(self.login_win, text="Регистрация", command=self.show_register_window, bd=0, fg="blue").pack()

    def process_login(self):
        u = self.ent_login.get()
        p = self.ent_pass.get()
        try:
            r = requests.post(f"{BASE_URL}/login", json={"username": u, "password": p})
            if r.status_code == 200:
                res = r.json()
                if res.get("status") == "success":
                    self.current_user = res["user"]
                    self.login_win.destroy()
                    self.setup_main_ui() # Строим главное окно
                    self.root.deiconify() # Показываем его
                else:
                    messagebox.showerror("Ошибка", res.get("message"))
            else:
                messagebox.showerror("Ошибка", "Неверные данные")
        except Exception as e:
            messagebox.showerror("Ошибка связи", f"Сервер недоступен: {e}")

    def show_register_window(self):
        reg_win = tk.Toplevel(self.login_win)
        reg_win.title("Регистрация")
        reg_win.geometry("300x350")
        
        tk.Label(reg_win, text="Логин:").pack(pady=2)
        ent_u = tk.Entry(reg_win); ent_u.pack()

        tk.Label(reg_win, text="Email:").pack(pady=2)
        ent_e = tk.Entry(reg_win); ent_e.pack()

        tk.Label(reg_win, text="Пароль:").pack(pady=2)
        ent_p = tk.Entry(reg_win, show="*"); ent_p.pack()

        def submit():
            data = {"username": ent_u.get(), "email": ent_e.get(), "password": ent_p.get()}
            try:
                r = requests.post(f"{BASE_URL}/register", json=data)
                if r.status_code == 200:
                    messagebox.showinfo("Успех", "Аккаунт создан! Теперь войдите.")
                    reg_win.destroy()
                elif r.status_code == 422:
                     messagebox.showerror("Ошибка", "Неверный формат почты (забыли @?)")
                else:
                    try:
                        msg = r.json().get("message", r.text)
                    except:
                        msg = r.text
                    messagebox.showerror("Ошибка", f"Сервер: {msg}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Сбой сети: {e}")

        tk.Button(reg_win, text="Создать аккаунт", command=submit, bg="#e1ebe1").pack(pady=15)

    # ---------------------------------------------------------
    # 2. ГЛАВНЫЙ ИНТЕРФЕЙС (Твой старый код + Скрипт товарища)
    # ---------------------------------------------------------
    def setup_main_ui(self):
        # Верхняя панель инфо
        top_frame = tk.Frame(self.root, pady=10, bg="#f0f0f0")
        top_frame.pack(fill="x")
        
        tk.Label(top_frame, text=f"Пользователь: {self.current_user['username']}", bg="#f0f0f0", font=("Arial", 10, "bold")).pack(side="left", padx=10)
        self.lbl_balance = tk.Label(top_frame, text=f"Баланс: {self.current_user['points']} баллов", bg="#f0f0f0", fg="green", font=("Arial", 10, "bold"))
        self.lbl_balance.pack(side="right", padx=10)
        
        tk.Button(top_frame, text="Выйти", command=self.logout, font=("Arial", 8)).pack(side="right", padx=5)

        # Вкладки
        notebook = ttk.Notebook(self.root)
        notebook.pack(expand=True, fill="both", padx=5, pady=5)

        # --- ВКЛАДКА 1: ЗАКАЗЧИК (Здесь внедряем act.py) ---
        frame_customer = tk.Frame(notebook)
        notebook.add(frame_customer, text="Разместить заказ")

        lb_frame = tk.LabelFrame(frame_customer, text="Новое задание", padx=15, pady=15)
        lb_frame.pack(fill="x", padx=10, pady=10)

        tk.Label(lb_frame, text="Название товара/услуги:").grid(row=0, column=0, sticky="w")
        self.ent_title = tk.Entry(lb_frame, width=40)
        self.ent_title.grid(row=0, column=1, pady=5)

        tk.Label(lb_frame, text="Ссылка (URL):").grid(row=1, column=0, sticky="w")
        self.ent_url = tk.Entry(lb_frame, width=40)
        self.ent_url.grid(row=1, column=1, pady=5)

        tk.Label(lb_frame, text="Кол-во просмотров:").grid(row=2, column=0, sticky="w")
        self.ent_count = tk.Entry(lb_frame, width=10)
        self.ent_count.grid(row=2, column=1, sticky="w", pady=5)
        self.ent_count.insert(0, "10")

        # КНОПКА С ИНТЕГРАЦИЕЙ
        self.btn_create = tk.Button(lb_frame, text="1. Проверить ссылку (Браузер) -> 2. Купить", 
                                    bg="orange", fg="black", font=("Arial", 10, "bold"),
                                    command=self.start_creation_with_script)
        self.btn_create.grid(row=3, columnspan=2, pady=15)

        # Таблица моих заказов (из старого кода)
        tk.Label(frame_customer, text="Мои активные заказы:").pack(pady=(10,0))
        self.my_orders_tree = ttk.Treeview(frame_customer, columns=("ID", "Title", "Progress"), show="headings", height=8)
        self.my_orders_tree.heading("ID", text="#")
        self.my_orders_tree.heading("Title", text="Название")
        self.my_orders_tree.heading("Progress", text="Прогресс")
        self.my_orders_tree.pack(fill="both", expand=True, padx=10, pady=5)
        
        tk.Button(frame_customer, text="Обновить список", command=self.load_all_orders).pack(pady=5)


        # --- ВКЛАДКА 2: ИСПОЛНИТЕЛЬ (Твой старый код) ---
        frame_worker = tk.Frame(notebook)
        notebook.add(frame_worker, text="Заработать (+5)")
        
        self.tasks_tree = ttk.Treeview(frame_worker, columns=("ID", "Title"), show="headings")
        self.tasks_tree.heading("ID", text="ID")
        self.tasks_tree.heading("Title", text="Задание")
        self.tasks_tree.pack(fill="both", expand=True, padx=10, pady=10)

        btn_box = tk.Frame(frame_worker)
        btn_box.pack(pady=5)
        tk.Button(btn_box, text="Обновить задачи", command=self.load_available_tasks).pack(side="left", padx=5)
        tk.Button(btn_box, text="ВЫПОЛНИТЬ", bg="#fff3cd", command=self.complete_task_logic).pack(side="left", padx=5)

        # Инициализация данных
        self.load_all_orders()
        self.load_available_tasks()

    # ---------------------------------------------------------
    # 3. ЛОГИКА (Склеиваем всё вместе)
    # ---------------------------------------------------------
    
    def start_creation_with_script(self):
        """Запускает поток, чтобы интерфейс не завис пока браузер работает"""
        threading.Thread(target=self.process_order_creation, daemon=True).start()

    def process_order_creation(self):
        title = self.ent_title.get()
        url = self.ent_url.get()
        try:
            count = int(self.ent_count.get())
        except:
            messagebox.showerror("Ошибка", "Количество должно быть числом")
            return

        if not title or not url:
            messagebox.showwarning("Ошибка", "Заполните все поля!")
            return

        # Блокируем кнопку
        self.btn_create.config(state="disabled", text="Работает скрипт проверки...")

        # 1. ЗАПУСК СКРИПТА ТОВАРИЩА
        try:
            print(f"Запускаем act.run_validation для {url}")
            is_valid = act.run_validation(url) # <-- ВЫЗОВ ФУНКЦИИ ИЗ act.py
        except Exception as e:
            print(f"Ошибка скрипта: {e}")
            is_valid = False

        # 2. ЕСЛИ УСПЕХ -> ОТПРАВЛЯЕМ НА СЕРВЕР
        if is_valid:
            self.btn_create.config(text="Сохранение заказа...")
            payload = {
                "user_id": self.current_user["id"],
                "title": title,
                "target_url": url,
                "views_count": count
            }
            try:
                r = requests.post(f"{BASE_URL}/orders/create", json=payload)
                if r.status_code == 200:
                    res = r.json()
                    if res.get("status") == "success":
                        messagebox.showinfo("Успех", "Заказ создан и баллы списаны!")
                        
                        # Очищаем поля ввода
                        self.ent_title.delete(0, tk.END)
                        self.ent_url.delete(0, tk.END)
                        
                        # Вызываем обновление данных пользователя
                        self.update_user_info() 
                        # Обновляем список заказов
                        self.load_all_orders()  
                    else:
                        messagebox.showerror("Ошибка", res.get("message"))
                else:
                    messagebox.showerror("Ошибка", f"HTTP {r.status_code}: {r.text}")
            except Exception as e:
                messagebox.showerror("Ошибка связи", str(e))
        else:
            messagebox.showerror("Провал", "Скрипт проверки не смог обработать ссылку.\nВозможно, страница недоступна или бот был закрыт.")

        # Разблокируем кнопку
        self.btn_create.config(state="normal", text="1. Проверить ссылку (Браузер) -> 2. Купить")

    def update_user_info(self):
        try:
            # Запрашиваем актуальные данные о пользователе с сервера
            r = requests.get(f"{BASE_URL}/users/{self.current_user['id']}")
            if r.status_code == 200:
                new_data = r.json()
                # Обновляем локальный объект пользователя
                self.current_user = new_data
                
                # Обновляем текст на экране. 
                # Важно: в main.py поле называется 'balance', проверьте это!
                new_balance = new_data.get('balance', 0)
                self.lbl_balance.config(text=f"Баланс: {new_balance} баллов")
                print(f"Интерфейс обновлен: новый баланс {new_balance}")
        except Exception as e:
            print(f"Не удалось обновить баланс в интерфейсе: {e}")

    def load_all_orders(self):
        # Загрузка для таблицы мониторинга
        for i in self.my_orders_tree.get_children(): self.my_orders_tree.delete(i)
        try:
            r = requests.get(f"{BASE_URL}/orders/all")
            for o in r.json():
                # Показываем: ID, Название, Прогресс (Сделано / Лимит)
                prog = f"{o['views_done']} / {o['views_limit']}"
                self.my_orders_tree.insert("", "end", values=(o["id"], o["title"], prog))
        except: pass

    def load_available_tasks(self):
        for i in self.tasks_tree.get_children(): self.tasks_tree.delete(i)
        try:
            r = requests.get(f"{BASE_URL}/tasks/available/{self.current_user['id']}")
            for t in r.json():
                self.tasks_tree.insert("", "end", values=(t["id"], t["title"]))
        except: pass

    def complete_task_logic(self):
        sel = self.tasks_tree.selection()
        if not sel: return
        t_id = self.tasks_tree.item(sel[0])["values"][0]
        try:
            r = requests.post(f"{BASE_URL}/tasks/complete", json={"user_id": self.current_user['id'], "order_id": t_id})
            res = r.json()
            if res.get("status") == "success":
                messagebox.showinfo("Готово", "+5 баллов!")
                self.update_user_info()
                self.load_available_tasks()
            else:
                messagebox.showerror("Упс", res.get("message"))
        except: pass

    def logout(self):
        self.current_user = None
        # Уничтожаем все виджеты главного окна
        for widget in self.root.winfo_children():
            widget.destroy()
        # Скрываем корень и показываем логин заново
        self.root.withdraw()
        self.show_login_window()

if __name__ == "__main__":
    root = tk.Tk()
    app = MainApp(root)
    root.mainloop()