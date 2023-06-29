import tkinter as tk
from tkinter import ttk, filedialog
import dirAnalysis
import io
from PIL import Image, ImageTk

da = dirAnalysis.DirAnalysis()

class MetaWaveGUI(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Music App")
        self.geometry("1100x600")
        self.resizable(False, False)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Создание левого блока с поиском
        search_frame = ttk.Frame(self, style="Search.TFrame")
        style = ttk.Style()
        search_frame.grid(row=0, column=0, sticky="ns")
        search_frame.grid_rowconfigure(0, weight=0)
        search_frame.grid_columnconfigure(0, weight=1)

        style.configure("Search.TFrame", background="light gray")
        style.configure("Search.TLabel", background="light gray", font=("TkDefaultFont", 14, "bold"))

        search_label = ttk.Label(search_frame, text="Поиск", style="Search.TLabel")
        search_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        search_entry = ttk.Entry(search_frame, width=50)
        search_entry.grid(row=1, column=0, padx=10, pady=10, sticky="w")

        search_option = ttk.Combobox(search_frame, values=["Название файла", "Название песни", "Альбом", "Артист", "Жанр", "Год"])
        search_option.set("Название файла")
        search_option.grid(row=2, column=0, padx=10, pady=10, sticky="w")

        search_button = ttk.Button(search_frame, text="Найти", command=lambda: self.search_songs(search_entry.get(), search_option.get()))
        search_button.grid(row=3, column=0, padx=10, pady=(10, 0), sticky="w")

        self.message_label = ttk.Label(search_frame,background="light gray", foreground="red", font=("TkDefaultFont", 12))
        self.message_label.grid(row=5, column=0, padx=10, pady=10, sticky="w")

        filter_label = ttk.Label(search_frame, text="Фильтр", style="Search.TLabel")
        filter_label.grid(row=6, column=0, padx=10, pady=10, sticky="w")

        filter_option = ttk.Combobox(search_frame, values=["По алфавиту: а-я", "По алфавиту: я-а", "Сначала новые", "Сначала старые"])
        filter_option.set("По алфавиту: а-я")
        filter_option.grid(row=7, column=0, padx=10, pady=10, sticky="w")

        filter_button = ttk.Button(search_frame, text="Применить", command=lambda: self.filter_songs(filter_option.get()))
        filter_button.grid(row=8, column=0, padx=10, pady=10, sticky="w")

        close_button = ttk.Button(search_frame, text="Отменить", command=lambda: self.close_search())
        close_button.grid(row=9, column=0, padx=10, pady=(100, 0), sticky="w")

        # Создание правого блока с песнями и кнопкой
        self.songs_frame = ttk.Frame(self)
        self.songs_frame.grid(row=0, column=1, sticky="nsew")

        self.songs_frame.grid_rowconfigure(0, weight=0)
        self.songs_frame.grid_rowconfigure(1, weight=1)
        self.songs_frame.grid_columnconfigure(0, weight=1)

        ttk.Button(self.songs_frame, text="Открыть папку", command=self.open_folder).grid(
            row=0, column=0, padx=10, pady=10, sticky="e"
        )

        ttk.Button(self.songs_frame, text="Экспорт в csv", command=self.export_csv).grid(
            row=2, column=0, padx=10, pady=10, sticky="w"
        )

        self.canvas = tk.Canvas(self.songs_frame)
        self.canvas.grid(row=1, column=0, sticky="nsew")

        self.songs_frame_inner = ttk.Frame(self.canvas)
        self.songs_frame_window = self.canvas.create_window((0, 0), window=self.songs_frame_inner, anchor="nw")

        songs_scrollbar = ttk.Scrollbar(self.songs_frame, orient="vertical", command=self.canvas.yview)
        songs_scrollbar.grid(row=1, column=1, sticky="ns")
        self.canvas.config(yscrollcommand=songs_scrollbar.set)

        self.songs_frame_inner.bind("<Configure>", self.update_canvas_scrollregion)

        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        da.creat_db("audiofile.db")
        songs = da.output_all_data_db("audiofile.db")
        if len(songs) != 0:
            self.load_songs(songs)

    def search_songs(self, search_query, search_option):
      
        if search_query == "":
            self.message_label.configure(text="Нужно ввести запрос!")
        elif search_query != "":
            self.message_label.configure(text="")
            if search_option == "Название файла":
                data = da.search("audiofile.db", "name", search_query)
            elif search_option == "Название песни":
                data = da.search("audiofile.db", "title", search_query)
            elif search_option == "Альбом":
                data = da.search("audiofile.db", "album", search_query)
            elif search_option == "Артист":
                data = da.search("audiofile.db", "artist", search_query)
            elif search_option == "Жанр":
                data = da.search("audiofile.db", "genre", search_query)
            elif search_option == "Год":
                data = da.search("audiofile.db", "year", search_query)

            if len(data) == 0:
                da.cancel_search()
                self.message_label.configure(text="По вашему запросу ничего не найдено")
            else:
                self.load_songs(data)

    def filter_songs(self, filter_option):
        if filter_option == "По алфавиту: а-я":
            data = da.filter("audiofile.db", "name", True)
        elif filter_option == "По алфавиту: я-а":
            data = da.filter("audiofile.db", "name", False)
        elif filter_option == "Сначала новые":
            data = da.filter("audiofile.db", "year", False)
        elif filter_option == "Сначала старые":
            data = da.filter("audiofile.db", "year", True)

        self.load_songs(data)

    def close_search(self):
        da.cancel_search()
        songs = da.output_all_data_db("audiofile.db")
        self.load_songs(songs)

    def load_songs(self, songs):

        for widget in self.songs_frame_inner.winfo_children():
            widget.destroy()

        num_songs = len(songs)
        max_cols = 4
        max_rows = (num_songs + max_cols - 1) // max_cols

        self.songs_frame_inner.grid_rowconfigure(list(range(max_rows)), weight=1)
        self.songs_frame_inner.grid_columnconfigure(list(range(max_cols)), weight=1)

        for i, song in enumerate(songs):
            song_frame = ttk.Frame(self.songs_frame_inner, width=200, height=200)
            song_frame.grid(row=i // max_cols, column=i % max_cols, padx=10, pady=10, sticky="nsew")

            if song[1] is None:
                im = Image.open("temp\cover.jpg")
                im.thumbnail((150, 150))
                cover_image = ImageTk.PhotoImage(im)
                cover_label = ttk.Label(song_frame, image=cover_image)
                cover_label.image = cover_image
                cover_label.pack()
                im.close()
            else:
                image_stream = io.BytesIO(song[1])
                im = Image.open(image_stream)
                im.thumbnail((150, 150))
                cover_image = ImageTk.PhotoImage(im)
                cover_label = ttk.Label(song_frame, image=cover_image)
                cover_label.image = cover_image
                cover_label.pack()
                im.close()

            title_label = ttk.Label(song_frame, text=song[0], font=("TkDefaultFont", 11), wraplength=180)
            title_label.pack()

            cover_label.bind("<Button-1>", lambda e, s=song: self.show_song_details(s))

        self.songs_frame_inner.update_idletasks()
        
        if self.songs_frame_inner.winfo_reqwidth() > self.canvas.winfo_width():
            self.canvas.config(scrollregion=self.canvas.bbox("all"))
        else:
            self.canvas.config(scrollregion="")
        
    def show_song_details(self, song):
        details_window = tk.Toplevel(self)
        details_window.title("Данные о песне")
        details_window.geometry("650x650")
        details_window.resizable(False, False)
        
        screen_width = details_window.winfo_screenwidth()
        screen_height = details_window.winfo_screenheight()
        window_width = details_window.winfo_reqwidth()
        window_height = details_window.winfo_reqheight()
        position_x = int(screen_width / 4 - window_width / 4)
        position_y = int(screen_height / 4 - window_height / 4)
        details_window.geometry(f"+{position_x+50}+{position_y-100}")
        
        ttk.Label(details_window, text="Название:", font=("TkDefaultFont", 12)).grid(row=2, column=0, padx=(10, 0), sticky="w")
        ttk.Label(details_window, text="Альбом:", font=("TkDefaultFont", 12)).grid(row=3, column=0, padx=(10, 0), sticky="w")
        ttk.Label(details_window, text="Артист:", font=("TkDefaultFont", 12)).grid(row=4, column=0, padx=(10, 0), sticky="w")
        ttk.Label(details_window, text="Жанр:", font=("TkDefaultFont", 12)).grid(row=5, column=0, padx=(10, 0), sticky="w")
        ttk.Label(details_window, text="Год:", font=("TkDefaultFont", 12)).grid(row=6, column=0, padx=(10, 0), sticky="w")
        ttk.Label(details_window, text="Формат аудио:", font=("TkDefaultFont", 12)).grid(row=7, column=0, padx=(10, 0), sticky="w")
        ttk.Label(details_window, text="Длитеоьность трека:", font=("TkDefaultFont", 12)).grid(row=8, column=0, padx=(10, 0), sticky="w")
        ttk.Label(details_window, text="Количество каналов:", font=("TkDefaultFont", 12)).grid(row=9, column=0, padx=(10, 0), sticky="w")
        ttk.Label(details_window, text="Битрейт:", font=("TkDefaultFont", 12)).grid(row=10, column=0, padx=(10, 0), sticky="w")
        ttk.Label(details_window, text="Частота:", font=("TkDefaultFont", 12)).grid(row=11, column=0, padx=(10, 0), sticky="w")
        ttk.Label(details_window, text="Размер файла:", font=("TkDefaultFont", 12)).grid(row=12, column=0, padx=(10, 0), sticky="w")
        ttk.Label(details_window, text="Спектрограмма:", font=("TkDefaultFont", 12)).grid(row=13, column=0, padx=(10, 0), sticky="w")
        
        title_label = ttk.Label(details_window, text=song[0], font=("TkDefaultFont", 12, "bold"))
        title_label.grid(row=0, column=1)

        if song[1] is None:
            im = Image.open("temp\cover.jpg")
            im.thumbnail((200, 200))
            cover_image = ImageTk.PhotoImage(im)
            cover_label = ttk.Label(details_window, image=cover_image)
            cover_label.image = cover_image
            cover_label.grid(row=1, column=1)
            im.close()
        else:
            image_stream = io.BytesIO(song[1])
            im = Image.open(image_stream)
            im.thumbnail((200, 200))
            cover_image = ImageTk.PhotoImage(im)
            cover_label = ttk.Label(details_window, image=cover_image)
            cover_label.image = cover_image
            cover_label.grid(row=1, column=1)
            im.close()    

        ttk.Label(details_window, text=song[2], font=("TkDefaultFont", 12)).grid(row=2, column=1, columnspan=2, sticky="w")
        ttk.Label(details_window, text=song[3], font=("TkDefaultFont", 12)).grid(row=3, column=1, columnspan=2, sticky="w")
        ttk.Label(details_window, text=song[4], font=("TkDefaultFont", 12)).grid(row=4, column=1, columnspan=2, sticky="w")
        ttk.Label(details_window, text=song[5], font=("TkDefaultFont", 12)).grid(row=5, column=1, columnspan=2, sticky="w")
        ttk.Label(details_window, text=song[6], font=("TkDefaultFont", 12)).grid(row=6, column=1, columnspan=2, sticky="w")
        ttk.Label(details_window, text=song[7], font=("TkDefaultFont", 12)).grid(row=7, column=1, columnspan=2, sticky="w")
        ttk.Label(details_window, text=song[8], font=("TkDefaultFont", 12)).grid(row=8, column=1, columnspan=2, sticky="w")
        ttk.Label(details_window, text=song[9], font=("TkDefaultFont", 12)).grid(row=9, column=1, columnspan=2, sticky="w")
        ttk.Label(details_window, text=song[10], font=("TkDefaultFont", 12)).grid(row=10, column=1, columnspan=2, sticky="w")
        ttk.Label(details_window, text=song[11], font=("TkDefaultFont", 12)).grid(row=11, column=1, columnspan=2, sticky="w")
        ttk.Label(details_window, text=song[12], font=("TkDefaultFont", 12)).grid(row=12, column=1, columnspan=2, sticky="w")

        image_stream = io.BytesIO(song[13])
        im = Image.open(image_stream)
        im.thumbnail((500, 500))
        cover_image = ImageTk.PhotoImage(im)
        cover_label = ttk.Label(details_window, image=cover_image)
        cover_label.image = cover_image
        cover_label.grid(row=13, column=1, columnspan=2)
        im.close()
        
        details_window.transient(self)
        details_window.grab_set()
        self.wait_window(details_window)

    def open_folder(self):
        folder = filedialog.askdirectory()

        modal_window = tk.Toplevel(self)
        modal_window.title("Открыть папку")
        modal_window.geometry("300x180")
        modal_window.resizable(False, False)
        modal_window.transient(self)


        screen_width = modal_window.winfo_screenwidth()
        screen_height = modal_window.winfo_screenheight()
        window_width = modal_window.winfo_reqwidth()
        window_height = modal_window.winfo_reqheight()
        position_x = int((screen_width / 2) - (window_width / 2))
        position_y = int((screen_height / 2) - (window_height / 2))
        modal_window.geometry(f"+{position_x}+{position_y}") 


        ttk.Label(modal_window, text="Типы файлов:").grid(row=1, column=0, pady=(40, 10), sticky="e")
        ttk.Label(modal_window, text="Исключения:").grid(row=2, column=0, sticky="e")

        file_types_entry = ttk.Entry(modal_window, width=30)
        file_types_entry.grid(row=1, column=1, padx=5, pady=(40, 10))

        exception_entry = ttk.Entry(modal_window, width=30)
        exception_entry.grid(row=2, column=1, padx=5, pady=(5, 15)) 

        def close_modal():
            modal_window.destroy()

        open_button = ttk.Button(modal_window, text="Открыть", command=lambda: [self.update_db_and_songs(folder, file_types_entry.get(), exception_entry.get()), close_modal()])
        open_button.grid(row=3, column=1)

        modal_window.grab_set()
        self.wait_window(modal_window)

    def export_csv(self):
        file = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")])
        da.export_csv(file, "audiofile.db")
        

    def update_db_and_songs(self, path, file_types, exception):
        if path != "":
            if file_types == "":
                file_types = [".mp3", ".aiff", ".flac"]
            else:
                file_types = file_types.split(",")
                for i in range(len(file_types)):
                    file_types[i] = file_types[i].strip()

            if exception == "":
                exception = list()
            else:
                exception = exception.split(",")
                for i in range(len(exception)):
                    exception[i] = exception[i].strip()

            da.set_data(path, "audiofile.db", file_types, exception)
            songs = da.output_all_data_db("audiofile.db")
            self.load_songs(songs)


    def update_canvas_scrollregion(self, event):
        self.canvas.config(scrollregion=self.canvas.bbox("all"))
    
    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

if __name__ == "__main__":
    app = MetaWaveGUI()
    app.mainloop()