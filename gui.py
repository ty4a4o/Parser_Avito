import tkinter as tk
import io
import requests
import Parser_sel as parser # Предполагается, что это ваш модуль парсинга
import ttkbootstrap as btk
from tkinter import ttk, messagebox
from threading import Thread
from PIL import Image, ImageTk, ImageFilter, ImageDraw, ImageFont # Добавим ImageFilter
from ttkbootstrap.constants import *

class AvitoParserGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Avito Parser")
        self.root.geometry("850x600")
        
        # Настройка темы
        self.style = btk.Style(theme='darkly')
        
        self.create_widgets()

    def create_widgets(self):
        # Фрейм для управления (верхняя часть)
        control_frame = btk.Frame(self.root, padding=10)
        control_frame.pack(side="top", fill="x", padx=10, pady=10)

        # Кнопка для открытия модального окна
        # Используем шрифт темы для лучшей интеграции
        add_button = btk.Button(control_frame, text="Создать новую заявку", command=self.open_modal_window, bootstyle="info")
        add_button.pack(pady=10)
        
        # Фрейм-контейнер для карточек
        # Используем Canvas с Scrollbar для возможности прокрутки карточек
        self.canvas = btk.Canvas(self.root, background=self.root.cget('bg'))
        self.scrollbar = btk.Scrollbar(self.root, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = btk.Frame(self.canvas, padding=10)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        self.scrollbar.pack(side="right", fill="y")

        # Назначаем scrollable_frame для карточек
        self.card_container = self.scrollable_frame
        
        # Метка статуса внизу
        self.status_label = btk.Label(self.root, text="Готов к работе", font=("-size 10"), bootstyle="secondary")
        self.status_label.pack(side="bottom", fill="x", pady=5)

    def open_modal_window(self):
        # Создание модального окна
        modal = btk.Toplevel(self.root)
        modal.title("Новая заявка")
        modal.transient(self.root)
        modal.grab_set()
        modal.focus_set()

        # Позиционирование окна по центру
        modal_width = 950
        modal_height = 200
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width / 2) - (modal_width / 2)
        y = (screen_height / 2) - (modal_height / 2)
        modal.geometry(f'{modal_width}x{modal_height}+{int(x)}+{int(y)}')
        
        modal_frame = btk.Frame(modal, padding=20)
        modal_frame.pack(expand=True, fill="both")
        
        # Поле для ввода URL
        btk.Label(modal_frame, text="URL объявления:", font="-size 11").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        url_entry = btk.Entry(modal_frame, width=90)
        url_entry.grid(row=0, column=1, padx=5, pady=5)
        url_entry.insert(0, "")

        # Поле для ввода имени автора
        btk.Label(modal_frame, text="Имя автора:", font="-size 11").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        author_entry = btk.Entry(modal_frame, width=90)
        author_entry.grid(row=1, column=1, padx=5, pady=5)
        author_entry.insert(0, "Алексей")

        # Кнопка "Создать"
        create_button = btk.Button(modal_frame, text="Создать", command=lambda: self.start_parsing(url_entry.get(), author_entry.get(), modal), bootstyle="success")
        create_button.grid(row=2, column=0, columnspan=2, pady=15)

    def start_parsing(self, url, author, modal):
        if not url or not author:
            messagebox.showwarning("Предупреждение", "Пожалуйста, заполните все поля.", parent=modal)
            return

        modal.destroy()  # Закрываем модальное окно

        self.set_status("Подождите, идёт парсинг...", "info")
        
        # Запуск парсинга в отдельном потоке
        Thread(target=self._run_parsing_thread, args=(url, author)).start()

    def _run_parsing_thread(self, url, author):
        # Эта функция выполняется в отдельном потоке
        try:
            # Предполагается, что parser.parse_avito_page(url) возвращает dict
            result = parser.parse_avito_page(url) 
        except Exception as e:
            # Обработка исключений, которые могут возникнуть в парсере
            result = {"error": f"Ошибка парсинга: {e}"}

        # Планируем вызов функции обновления интерфейса в основном потоке
        self.root.after(0, self.update_gui_with_result, result, author)

    def update_gui_with_result(self, result, author):
        # Эта функция выполняется в основном потоке GUI
        if "error" in result:
            self.set_status(f"❌ Ошибка: {result['error']}", "danger")
            messagebox.showerror("Ошибка парсинга", f"Произошла ошибка: {result['error']}")
        else:
            self.create_item_card(result, author)
            self.set_status("✅ Объявление успешно выложено!", "success")
            
    def create_item_card(self, data, author):
        # Используем card_container, который теперь является self.scrollable_frame
        card = btk.Frame(self.card_container, padding=10, bootstyle="secondary")
        card.pack(fill="x", padx=5, pady=5)
        
        # Сохранение данных в карточке для возможности редактирования/удаления
        card.data = data
        card.author = author

        # Левая часть: фото
        photo_frame = btk.Frame(card)
        photo_frame.pack(side="left", padx=10, pady=5)
        
        photo_url = data.get("photos", [None])[0]
        
        photo = None
        if photo_url and photo_url != "Фото не найдены":
            try:
                response = requests.get(photo_url, timeout=5) # Добавим таймаут
                img_data = response.content
                img = Image.open(io.BytesIO(img_data))
                
                # Используем Image.Resampling.LANCZOS для современных версий Pillow (или просто Image.LANCZOS)
                img.thumbnail((150, 150), Image.LANCZOS) 
                photo = ImageTk.PhotoImage(img)
                
            except Exception as e:
                print(f"Не удалось загрузить фото: {e}")
                photo_url = None # Установим в None, чтобы показать заглушку

        if photo:
            photo_label = btk.Label(photo_frame, image=photo, bootstyle="inverse-light")
            photo_label.image = photo  # Важно сохранить ссылку
            photo_label.pack()
        else:
            # Заглушка, если фото не найдено
            photo_label = btk.Label(photo_frame, text="Фото\nне найдено", width=15, height=10, bootstyle="warning")
            photo_label.pack()

        # Правая часть: текст и кнопки
        info_frame = btk.Frame(card)
        info_frame.pack(side="left", padx=10, pady=5, expand=True, fill="x")

        # Заголовок
        title_label = btk.Label(info_frame, text=data.get("title", "Нет заголовка"), font="-size 14 -weight bold", bootstyle="inverse-light", wraplength=400)
        title_label.pack(anchor="w", pady=2)
        
        # Автор
        author_label = btk.Label(info_frame, text=f"Автор: {author}", font="-size 12", bootstyle="inverse-light")
        author_label.pack(anchor="w", pady=2)
        
        # Добавим цену и город
        price_text = data.get("price", "Цена не указана")
        location_text = data.get("location", "Город не указан")
        btk.Label(info_frame, text=f"Цена: {price_text} | Город: {location_text}", font="-size 10", bootstyle="inverse-light").pack(anchor="w", pady=2)

        # Кнопки для разработчика
        buttons_frame = btk.Frame(card)
        buttons_frame.pack(side="right", padx=10, pady=5)
        
        # Кнопка "Изменить"
        edit_button = btk.Button(buttons_frame, text="✎", width=3, command=lambda c=card: self.edit_card(c), bootstyle="primary")
        edit_button.pack(side="top", pady=5)
        
        # Кнопка "Удалить"
        delete_button = btk.Button(buttons_frame, text="✖", width=3, command=lambda c=card: self.delete_card(c), bootstyle="danger")
        delete_button.pack(side="top", pady=5)
        
        # Обновление области прокрутки после добавления новой карточки
        self.root.after(100, lambda: self.canvas.configure(scrollregion=self.canvas.bbox("all")))


    def set_status(self, text, style):
        # Используем метод config для изменения стиля
        self.status_label.config(text=text, bootstyle=style) 
        
    def edit_card(self, card):
        messagebox.showinfo("Изменить", f"Функционал 'Изменить' пока не реализован.\nДанные: {card.data['title']}", parent=self.root)
        
    def delete_card(self, card):
        if messagebox.askyesno("Удалить", f"Вы уверены, что хотите удалить карточку '{card.data.get('title', 'Нет заголовка')}'?", parent=self.root):
            card.destroy()
            self.set_status("Карточка удалена.", "warning")
            # Обновление области прокрутки после удаления
            self.root.after(100, lambda: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

if __name__ == "__main__":
    root = btk.Window(themename="darkly") 
    app = AvitoParserGUI(root)
    root.mainloop()