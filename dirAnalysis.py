import os
import io
import csv
import sqlite3
import metaWave
from prettytable import from_db_cursor

meta = metaWave.MetaWave()

class DirAnalysis():

    __all_metadatas = list()
    __search_flac = False
    __search_query = ""

    def set_data(self, path_dir: str, path_db: str, type_file: list=[".mp3",".aiff",".flac"], exception: list=[]) -> None:
        '''Функция, которая получает данные о анализе папки и вызывает функции для создания бд,
        анализа дириктории и добавления данных в бд'''
        self.creat_db(path_db)
        self.__dir_analysis(path=path_dir, type_file=type_file, exeption=exception)
        self.__creat_or_updat_data_db(path_db, self.__all_metadatas)

    def creat_db(self, path: str) -> None:
        '''Функция, которая создает базу данных'''
        db = sqlite3.connect(path)
        cur = db.cursor()

        cur.execute('''
        CREATE TABLE IF NOT EXISTS audiofile (
            id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            name TEXT UNIQUE,   
            cover BLOB,
            title TEXT,
            album TEXT,
            artist TEXT,
            genre TEXT,
            year TEXT,
            audio_format TEXT,
            track_duration TEXT,
            count_chanels TEXT,
            bitrate INTEGER,
            sampling_rate INTEGER,
            file_size TEXT,
            spectrogram BLOB
            )
        ''')

        db.commit()
        db.close()

    def __dir_analysis(self, path: str, type_file: list, exeption: list, level: int=0) -> None:
        '''Функция, которая анализирует паку и дастает все метаданные из аудиофайлов'''
        dir = os.listdir(path)

        for object in dir:
            if os.path.isdir(path + '\\' + object):
                self.__dir_analysis(path=path + '\\' + object, type_file=type_file, exeption=exeption, level=level+1)
            else:
                if os.path.splitext(object)[1] in [".mp3",".aiff",".flac"]:
                    if os.path.splitext(object)[1] in type_file:
                        if len(exeption) != 0:
                            if object in exeption:
                                continue

                        metadatas = meta.get_metadata(path + '\\' + object)
                        self.__all_metadatas.append(metadatas)
                    else:
                        continue
                else:
                    continue

    def __creat_or_updat_data_db(self, path: str, all_metadatas: tuple) -> None:
        '''Функция, которая добавляет или обновляет данные в базе данных'''
        db = sqlite3.connect(path)
        cur = db.cursor()

        for metadatas in all_metadatas:
            cur.execute('SELECT * FROM audiofile WHERE name = ?', (metadatas[0],))
            row = cur.fetchone()

            if row is None:
                cur.execute("INSERT INTO audiofile (name, cover, title, album, artist, genre, year, audio_format, track_duration, count_chanels, bitrate, sampling_rate, file_size, spectrogram) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", metadatas)
            else:
                metadatas = list(metadatas)
                name = metadatas.pop(0)
                metadatas.append(name)
                metadatas = tuple(metadatas)
                cur.execute("UPDATE audiofile SET cover = ?, title = ?, album = ?, artist = ?, genre = ?, year = ?, audio_format = ?, track_duration = ?, count_chanels = ?, bitrate = ?, sampling_rate =  ?, file_size = ?, spectrogram = ? WHERE name = ?", metadatas)

        self.__all_metadatas = list()
        db.commit()
        db.close()

    def output_all_data_db(self, path: str) -> list:
        '''Функция, которая возврощает все данные из бд'''
        db = sqlite3.connect(path)
        cur = db.cursor()

        cur.execute("SELECT name, cover, title, album, artist, genre, year, audio_format, track_duration, count_chanels, bitrate, sampling_rate, file_size, spectrogram  FROM  audiofile")
        data = cur.fetchall()

        db.close()

        return data

    def output_name_data_db(self, path: str) -> None:
        '''Функция, которая выводит таблицу с именами файлов из бд'''
        db = sqlite3.connect(path)
        cur = db.cursor()

        cur.execute("SELECT name FROM  audiofile")
        print(from_db_cursor(cur))

        db.close()

    def search(self, path, type: str, search: str) -> list:
        db = sqlite3.connect(path)
        cur = db.cursor()
        self.__search_flac = True
        self.__search_query = f"SELECT name, cover, title, album, artist, genre, year, audio_format, track_duration, count_chanels, bitrate, sampling_rate, file_size, spectrogram FROM  audiofile WHERE {type} = '{search}'"

        cur.execute(f"SELECT name, cover, title, album, artist, genre, year, audio_format, track_duration, count_chanels, bitrate, sampling_rate, file_size, spectrogram FROM  audiofile WHERE {type} = ?", (search,))
        data = cur.fetchall()

        db.close()

        return data
    
    def cancel_search(self) -> None:
        self.__search_flac = False
        self.__search_query = ""
    
    def filter(self,path: str,  type_filter: str, increase: bool) -> list:
        db = sqlite3.connect(path)
        cur = db.cursor()

        if increase:
            query = f"ORDER BY {type_filter} ASC"
        else:
            query = f"ORDER BY {type_filter} DESC"

        if self.__search_flac:
            filter_query = self.__search_query + " " + query
            cur.execute(filter_query)
        else:
            cur.execute(f"SELECT name, cover, title, album, artist, genre, year, audio_format, track_duration, count_chanels, bitrate, sampling_rate, file_size, spectrogram FROM  audiofile {query}")
        data = cur.fetchall()

        db.close()

        return data
        
    def export_csv(self, path_csv: str, path_db: str) -> None:
        '''Функция, которая экспортирует данные из бд в csv'''
        db = sqlite3.connect(path_db)
        cur = db.cursor()
        all_datas = list()

        cur.execute("SELECT name, title, album, artist, genre, year, audio_format, track_duration, count_chanels, bitrate, sampling_rate, file_size FROM  audiofile")
        rows = cur.fetchall()

        for row in rows:
            data = dict()
            data["name"] = row[0]
            data["title"] = row[1]
            data["album"] = row[2]
            data["artist"] = row[3]
            data["genre"] = row[4]
            data["year"] = row[5]
            data["audio_format"] = row[6]
            data["track_duration"] = row[7]
            data["count_chanels"] = row[8]
            data["bitrate"] = row[9]
            data["sampling_rate"] = row[10]
            data["file_size"] = row[11]
            all_datas.append(data)

        header = ["name", "title", "album", "artist", "genre", "year", "audio_format", "track_duration", "count_chanels", "bitrate", "sampling_rate", "file_size"]

        with open(path_csv, "w") as f:
            writer = csv.DictWriter(f,lineterminator="\n", delimiter=";", fieldnames=header)
            writer.writeheader()
            writer.writerows(all_datas)

    def get_search(self, path, type: str, search: str) -> None:
        db = sqlite3.connect(path)
        cur = db.cursor()
        self.__search_flac = True
        self.__search_query = f"SELECT name, title, album, artist, genre, year, audio_format, track_duration, count_chanels, bitrate, sampling_rate, file_size FROM  audiofile WHERE {type} = '{search}'"

        cur.execute(f"SELECT name, title, album, artist, genre, year, audio_format, track_duration, count_chanels, bitrate, sampling_rate, file_size FROM  audiofile WHERE {type} = ?", (search,))
        print(from_db_cursor(cur))

        db.close()

    def get_search(self, path, type: str, search: str) -> None:
        db = sqlite3.connect(path)
        cur = db.cursor()
        self.__search_flac = True
        self.__search_query = f"SELECT name, title, album, artist, genre, year, audio_format, track_duration, count_chanels, bitrate, sampling_rate, file_size FROM  audiofile WHERE {type} = '{search}'"

        cur.execute(f"SELECT name, title, album, artist, genre, year, audio_format, track_duration, count_chanels, bitrate, sampling_rate, file_size FROM  audiofile WHERE {type} = ?", (search,))
        print(from_db_cursor(cur))

        db.close()

    def get_filter(self,path: str,  type_filter: str, increase: bool) -> None:
        db = sqlite3.connect(path)
        cur = db.cursor()

        if increase:
            query = f"ORDER BY {type_filter} ASC"
        else:
            query = f"ORDER BY {type_filter} DESC"

        if self.__search_flac:
            filter_query = self.__search_query + " " + query
            cur.execute(filter_query)
        else:
            cur.execute(f"SELECT name, title, album, artist, genre, year, audio_format, track_duration, count_chanels, bitrate, sampling_rate, file_size FROM  audiofile {query}")
        print(from_db_cursor(cur))

        db.close()

    
