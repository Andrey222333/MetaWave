import io
import os
import matplotlib
from mutagen import File
from mutagen.mp3 import MP3
from mutagen.flac import FLAC
from mutagen.aiff import AIFF
import matplotlib.pyplot as plt
import librosa
matplotlib.use('Agg')

class MetaWave:

    def get_metadata(self, file: str)-> tuple:
        '''Функция, которая достает метаданные из файлов. Поддерживаются файлы mp3, aiff, flac'''
        expansion = os.path.splitext(file)[1]

        if expansion == ".mp3":
            metadatas = self.get_metadata_mp3_aiff(file, "MP3")
        elif expansion == ".aiff":
            metadatas = self.get_metadata_mp3_aiff(file, "AIFF")
        elif expansion == ".flac":
            metadatas = self.get_metadata_flac(file)
        else:
            raise Exception('Такой тип файлов не поддерживается.')

        return metadatas

    def get_metadata_mp3_aiff(self, file: str, type_file: str) -> tuple:
        '''Функция, которая достает метаданные из файлов mp3 и aiff'''
        metadatas = list()

        if type_file == "MP3":
            audio = MP3(file)
        elif type_file == "AIFF":
            audio = AIFF(file)

        # Получение картинки обложки
        if 'APIC:' in audio:
            picture = audio['APIC:'].data  
        else:
            picture = None
        metadatas.append(picture)

        # Получение названия трека
        if "TIT2" in audio:
            title = audio.get("TIT2").text[0]
        else:
            title = None
        metadatas.append(title)

        # Получение альбома
        if "TALB" in audio:
            album = audio.get("TALB").text[0]
        else:
            album = None
        metadatas.append(album)

        # Получение артиста
        if "TPE1" in audio:
            artist = audio.get("TPE1").text[0]
        else:
            artist = None
        metadatas.append(artist)

        # Получение жанра
        if "TCON" in audio:
            genre = audio.get("TCON").text[0]
        else:
            genre = None
        metadatas.append(genre)

        # Получение года
        if "TDRC" in audio:
            year = audio.get("TDRC").text[0]
        else:
            year = None
        metadatas.append(year)

        additional_metadatas = self.get_additional_data(file)
        metadatas += additional_metadatas

        return tuple(metadatas)

    def get_metadata_flac(self, file: str) -> tuple:
        '''Функция, которая достает метаданные из файлов flac'''
        metadatas = list()
        audio = FLAC(file)

        # Получение обложки
        picture = audio.pictures
        if picture:
            for p in picture:
                if p.type == 3:
                    image = p.data
        else:
            image = None
        metadatas.append(image)

        # Получение названия трека
        if "title" in audio:
            title = audio["title"][0]
        else:
            title = None
        metadatas.append(title)

        # Получение альбома
        if "album" in audio:
            album = audio["album"][0]
        else:
            album = None
        metadatas.append(album)

        # Получение артиста
        if "artist" in audio:
            artist = audio["artist"][0]
        else:
            artist = None
        metadatas.append(artist)

        # Получение жанра
        if "genre" in audio:
            genre = audio["genre"][0]
        else:
            genre = None
        metadatas.append(genre)

        # Получение года
        if "year" in audio:
            year = audio["year"][0]
        else:
            year = None
        metadatas.append(year)

        additional_metadatas = self.get_additional_data(file)
        metadatas += additional_metadatas

        return tuple(metadatas)
    
    def get_additional_data(self, file: str) -> list:
        '''Функция которая достает дополнительные данные из аудиофайлов'''
        additional_metadatas = list()
        audio = File(file)

        # Получение формата аудио
        audio_format = audio.mime[0]
        additional_metadatas.append(audio_format.removeprefix("audio/"))

        # Получение длительности трека
        duration = audio.info.length
        minutes = int(duration // 60)
        seconds = int(duration % 60)
        additional_metadatas.append(f"{minutes} мин {seconds} сек")

        # Получение информации о количестве каналов
        count_channels = audio.info.channels
        if count_channels == 2:
            channel = "Стерео"
        elif count_channels == 1:
            channel = "Моно"
        else:
            channel = "Многоканальный"
        additional_metadatas.append(channel)

        # Получение битрейта
        bitrate = audio.info.bitrate
        additional_metadatas.append(bitrate)

        # Получение частоты дискретизации 
        sample_rate = audio.info.sample_rate
        additional_metadatas.append(sample_rate)

        # Получение размера файла
        size = os.stat(file).st_size
        additional_metadatas.append(self.file_size(size))

        spectrogram = self.get_spectrogram(file)
        additional_metadatas.append(spectrogram)

        return additional_metadatas
    
    def get_spectrogram(self, file) -> bytes:
        '''Функция, которая возвращает фотку спектрогррамы в байтах'''
        y, sr = librosa.load(file)

        plt.figure(figsize=(14, 5))
        librosa.display.waveshow(y, sr=sr,color = "b",label='Harmonic')
        byte_stream = io.BytesIO()

        plt.savefig(byte_stream, format='jpg')

        # Получите байты из потока
        byte_stream.seek(0)
        image_bytes = byte_stream.read()

        # Закройте поток
        byte_stream.close()

        return image_bytes

    def file_size(self, size_bytes: int) -> str:
        '''Функция для автоматической конвертации байтов в КБ, МБ, ГБ...'''
        units_measurement = ('B','KB','MB','GB','TB','PB')

        count = 0
        
        while size_bytes // 1024 != 0:
            if count == 5:
                break

            size_bytes /= 1024
            count += 1

        return str(round(size_bytes, 2)) + ' ' + units_measurement[count]
    
    def print_metadata(self, metadatas: tuple) -> None:
        '''Функция дял вывода метаданных из кортежа в консоль'''
        print(metadatas[0])
        print("Название трека:", metadatas[1])
        print("Альбом:", metadatas[2])
        print("Артист:", metadatas[3])
        print("Жанр:", metadatas[4])
        print("Год:", metadatas[5])
        print("Формат аудио:", metadatas[6])
        print("Длительность трека:", metadatas[7])
        print("Количество каналов:", metadatas[8])
        print("Битрейт:", metadatas[9], "кбит/сек")
        print("Частота дискретизации (Hz):", metadatas[10])
        print("Размер файла:", metadatas[11])
        print(metadatas[12])