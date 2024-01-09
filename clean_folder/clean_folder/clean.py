import os
import shutil
import re
import sys
from pathlib import Path



result = {
    "known_file_extens": [],
    "unknown_file_extens": [],
    "files_by_categories": {
        'images': [],
        'video': [],
        'documents': [],
        'audio': [],
        'archives': [],
        'other': [],

    },
}


def normalize(filename):
    # Транслітерація кириличного алфавіту та заміна символів
    CYRILLIC_SYMBOLS = "абвгдеёжзийклмнопрстуфхцчшщъыьэюяєіїґ"
    TRANSLATION = ("a", "b", "v", "g", "d", "e", "e", "j", "z", "i", "j", "k", "l", "m", "n", "o", "p", "r", "s", "t", "u",
                   "f", "h", "ts", "ch", "sh", "sch", "", "y", "", "e", "yu", "ya", "je", "i", "ji", "g")

    TRANS = {}

    for c, l in zip(CYRILLIC_SYMBOLS, TRANSLATION):
        TRANS[ord(c)] = l
        TRANS[ord(c.upper())] = l.upper()

    translated_name = filename.translate(TRANS)
    normalized_name = re.sub(r'[^a-zA-Z0-9]', '_', translated_name)

    return normalized_name


def if_file_exists(path_pointer: Path):
    # Функція призначена для обробки ситуації, коли файл з вказаною назвою вже існує у вказаній директорії
    f_name_origin = path_pointer.stem
    f_number = 1

    while path_pointer.exists():
        # Перевірка, чи існує вказівник на файл/директорію у визначеній директорії
        f_name = f_name_origin + "_" + str(f_number)
        path_pointer = path_pointer.with_stem(f_name)
        f_number += 1
    else:
        return path_pointer


def process_folder(folder_path):
    # Шляхи до категорій
    image_path = Path(folder_path, 'images')
    video_path = Path(folder_path, 'video')
    documents_path = Path(folder_path, 'documents')
    audio_path = Path(folder_path, 'audio')
    archives_path = Path(folder_path, 'archives')
    other_path = Path(folder_path, 'other')

    sorting_folders = [image_path, video_path,
                       documents_path, audio_path, archives_path, other_path]
    

    # Створення категорій, якщо вони не існують
    for folder in sorting_folders:
        os.makedirs(folder, exist_ok=True)


    for root, dirs, files in os.walk(folder_path):
        # Виключення певних папок з обробки
        dirs[:] = [d for d in dirs if Path(root, d) not in sorting_folders]

        if Path(root) not in sorting_folders:

            # Перебір усіх файлів у вказаній директорії та її піддиректоріях
            for filename in files:
                file_path = Path(root, filename)
                extension = filename.split('.')[-1].upper()

                # Отримуємо суфікс (розширення) файлу з крапкою (.txt)
                file_suffix = file_path.suffix

                # Отримуємо ім'я файлу без розширення
                file_stem = file_path.stem
                new_filename = normalize(file_stem) + file_suffix

                # Обробка розширення та переміщення файлу в відповідну категорію
                if extension in ['JPEG', 'PNG', 'JPG', 'SVG']:
                    p = Path(image_path, new_filename)
                    p = if_file_exists(p)
                    result['files_by_categories']['images'].append(str(p))
                    shutil.move(file_path, p)
                elif extension in ['AVI', 'MP4', 'MOV', 'MKV']:
                    p = Path(video_path, new_filename)
                    p = if_file_exists(p)
                    result['files_by_categories']['video'].append(str(p))
                    shutil.move(file_path, p)
                elif extension in ['DOC', 'DOCX', 'TXT', 'PDF', 'XLSX', 'PPTX']:
                    p = Path(documents_path, new_filename)
                    p = if_file_exists(p)
                    result['files_by_categories']['documents'].append(str(p))
                    shutil.move(file_path, p)
                elif extension in ['MP3', 'OGG', 'WAV', 'AMR']:
                    p = Path(audio_path, new_filename)
                    p = if_file_exists(p)
                    result['files_by_categories']['audio'].append(str(p))
                    shutil.move(file_path, p)
                elif extension in ['ZIP', 'GZ', 'TAR']:
                    try:
                        shutil.unpack_archive(file_path, Path(archives_path, file_stem))
                    except:
                        pass
                    finally:
                        os.remove(file_path)
                else:
                    p = Path(other_path, new_filename)
                    p = if_file_exists(p)
                    result['files_by_categories']['other'].append(str(p))
                    shutil.move(file_path, p)

                # Заповнення списку відомих та невідомих розширень
                if extension not in result['known_file_extens']:
                    result['known_file_extens'].append(extension)
                if extension not in ['JPEG', 'PNG', 'JPG', 'SVG', 'AVI', 'MP4', 'MOV', 'MKV',
                                     'DOC', 'DOCX', 'TXT', 'PDF', 'XLSX', 'PPTX', 'MP3', 'OGG', 'WAV', 'AMR',
                                     'ZIP', 'GZ', 'TAR']:
                    if extension not in result['unknown_file_extens']:
                        result['unknown_file_extens'].append(extension)

    # Видалення порожніх папок
    for root, dirs, files in os.walk(folder_path, topdown=False):
        for folder in dirs:
            folder_path = os.path.join(root, folder)
            if folder_path not in sorting_folders:
                if not os.listdir(folder_path):
                    os.rmdir(folder_path)


    # Код для збереження результатів у консоль або у файл
    for category, files in result['files_by_categories'].items():
        print(f"\n{category.capitalize()} files:")
        for file in files:
            print(f"  {file}")

    print("\nKnown file extensions:")
    for ext in result['known_file_extens']:
        print(f"  {ext}")

    print("\nUnknown file extensions:")
    for ext in result['unknown_file_extens']:
        print(f"  {ext}")

    # Збереження результатів у файл
    with open('result.txt', 'w') as f:
        for category, files in result['files_by_categories'].items():
            f.write(f"\n{category.capitalize()} files:\n")
            for file in files:
                f.write(f"  {file}\n")

        f.write("\nKnown file extensions:\n")
        for ext in result['known_file_extens']:
            f.write(f"  {ext}\n")

        f.write("\nUnknown file extensions:\n")
        for ext in result['unknown_file_extens']:
            f.write(f"  {ext}\n")


def display_results(result):
    # Для виведення списків файлів в кожній категорії та виведення списків відомих та невідомих розширень
    for category, files in result['files_by_categories'].items():
        print(f"\n{category.capitalize()} files:")
        for file in files:
            print(f"  {file}")

    print("\nKnown file extensions:")
    for ext in result['known_file_extens']:
        print(f"  {ext}")

    print("\nUnknown file extensions:")
    for ext in result['unknown_file_extens']:
        print(f"  {ext}")


def main():
    if len(sys.argv) != 2:
        print("Usage: python your_script.py /path/to/folder")
        sys.exit(1)
    target_folder = sys.argv[1]

    process_folder(target_folder)
    display_results(result)  # Додає цей рядок, щоб відобразити або зберегти результати


if __name__ == "__main__":
    main()