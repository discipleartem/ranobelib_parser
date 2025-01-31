from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import os

def setup_driver():
    """
    Настраивает и возвращает драйвер Chrome
    """
    options = webdriver.ChromeOptions()
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    # Убираем headless режим для видимости браузера
    prefs = {"profile.managed_default_content_settings.images": 2}
    options.add_experimental_option("prefs", prefs)

    # Используем стратегию загрузки "none", чтобы не ждать полной загрузки страницы
    options.page_load_strategy = 'none'

    return webdriver.Chrome(options=options)

def clean_text(text):
    """
    Удаляет строки, начинающиеся с "Переводчик"
    """
    lines = text.split("\n")
    cleaned_lines = [line for line in lines if not line.startswith("Переводчик")]
    return "\n".join(cleaned_lines)

def get_chapter_content(driver, chapter_num):
    """
    Получает содержимое главы, проверяя только загрузку ключевых элементов
    """
    url = f"https://ranobelib.me/ru/48886--alchemy-emperor-of-the-divine-dao/read/v1/c{chapter_num}"

    try:
        print(f"Открываем URL: {url}")
        driver.get(url)

        # Ждем появления заголовка <h1> и текста в <div class="text-content">
        try:
            wait = WebDriverWait(driver, 15)

            # Ждем заголовок <h1>
            chapter_title_element = wait.until(
                EC.presence_of_element_located((By.TAG_NAME, "h1"))
            )
            print("Заголовок главы найден.")

            # Ждем текст главы в <div class="text-content">
            chapter_text_element = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "main div.text-content"))
            )
            print("Основной текст главы найден.")
        except TimeoutException:
            print(f"Ключевые элементы не найдены для главы {chapter_num}. Пропуск.")
            return None

        # Извлекаем заголовок главы
        try:
            chapter_title = chapter_title_element.text.strip()
        except NoSuchElementException:
            chapter_title = f"Глава {chapter_num}"

        # Извлекаем текст главы
        try:
            paragraphs = chapter_text_element.find_elements(By.TAG_NAME, "p")
            chapter_text = "\n\n".join([p.text.strip() for p in paragraphs if p.text.strip()])
        except Exception as e:
            print(f"Ошибка при извлечении текста главы {chapter_num}: {e}")
            return None

        # Очищаем текст от строк, начинающихся с "Переводчик"
        chapter_text = clean_text(chapter_text)

        return f"\n\n{chapter_title}\n\n{chapter_text}"

    except Exception as e:
        print(f"Ошибка при обработке главы {chapter_num}: {e}")
        return None

def go_to_next_chapter(chapter_num):
    """
    Формирует URL следующей главы
    """
    return chapter_num + 1

def main():
    filename = "Император Алхимии Божественного Пути.txt"
    start_chapter = 1

    # Создаем файл если его нет
    if not os.path.exists(filename):
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("")

    driver = setup_driver()

    try:
        chapter_num = start_chapter
        consecutive_failures = 0
        max_failures = 3

        while consecutive_failures < max_failures:
            print(f"Загрузка главы {chapter_num}...")

            chapter_content = get_chapter_content(driver, chapter_num)

            if chapter_content:
                # Записываем главу в файл
                with open(filename, 'a', encoding='utf-8') as f:
                    f.write(chapter_content + "\n\n")

                print(f"Глава {chapter_num} успешно добавлена")

                # Переходим к следующей главе
                chapter_num = go_to_next_chapter(chapter_num)
                consecutive_failures = 0

                # Добавляем задержку между запросами
                time.sleep(2)
            else:
                # Если главу не удалось получить, записываем сообщение об ошибке
                with open(filename, 'a', encoding='utf-8') as f:
                    f.write(f"Глава {chapter_num} НЕ УДАЛОСЬ СКОПИРОВАТЬ !\n\n")

                print(f"Глава {chapter_num} НЕ УДАЛОСЬ СКОПИРОВАТЬ !")

                consecutive_failures += 1

                if consecutive_failures < max_failures:
                    print("Повторная попытка через 5 секунд...")
                    time.sleep(5)
                else:
                    print(f"Достигнуто максимальное количество неудачных попыток. Парсинг остановлен на главе {chapter_num}")
                    break

    finally:
        driver.quit()

if __name__ == "__main__":
    main()
