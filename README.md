# 🎬 YouTube Downloader Bot

Telegram-бот для скачивания видео и аудио с YouTube и других платформ. Проект построен на микросервисной архитектуре, где бот написан на Python, а сервис загрузки реализован на Go.

## 🏗️ Архитектура

Проект состоит из двух микросервисов:

1. **Сервис бота** (`cmd/bot`) 🤖  
   Реализован на Python с использованием библиотеки `aiogram`. Этот сервис отвечает за взаимодействие с пользователями Telegram, обработку команд и отправку запросов на скачивание.

2. **Сервис загрузки** (`cmd/downloader`) 📥  
   Реализован на Go. Этот сервис обрабатывает запросы на скачивание видео и аудио, используя `yt-dlp`, и возвращает результаты через gRPC.

Микросервисы взаимодействуют друг с другом через gRPC, обеспечивая высокую производительность и надежность.

## ✅ Требования

### Общие требования:
- Docker и Docker Compose (для запуска через контейнеры)
- Python 3.12 или новее (если запускать бот локально)
- Go 1.24 или новее (если запускать сервис загрузки локально)

### Зависимости Python:
- `aiogram`
- `telethon`
- `python-dotenv`
- `sqlalchemy`
- `asyncpg`
- `grpcio`
- `grpcio-tools`

### Зависимости Go:
- `google.golang.org/grpc`
- `google.golang.org/protobuf`
- `github.com/joho/godotenv`

## 🔧 Установка

1. Клонируйте репозиторий:

   ```bash
   git clone https://github.com/Fluorouacil/Go_Yt_Downloader_bot.git
   cd Go_Yt_Downloader_bot
   ```

2. Установите зависимости для Python:

   ```bash
   pip install -r requirements.txt
   ```

3. Установите зависимости для Go:

   ```bash
   go mod download
   ```

4. Создайте файл `.env` в корне проекта на основе .env.example

## 🚀 Запуск

### С использованием Docker Compose

1. Запустите все сервисы:

   ```bash
   docker-compose up --build
   ```

2. Бот будет доступен на порту `8000`, а gRPC-сервис загрузки — на порту `50051`.

### Локальный запуск

1. Убедитесь что у вас установлен yt-dlp и настроен PATH

   ```bash
   yt-dlp --version
   ```

2. Запустите сервис загрузки:

   ```bash
   go run cmd/downloader/main.go
   ```

3. В отдельном терминале запустите сервис бота:

   ```bash
   python main.py
   ```

## 📱 Использование

1. Отправьте боту ссылку на видео (например, с YouTube, Twitch, Instagram).
2. Бот предложит выбрать качество видео или формат аудио (если поддерживается).
3. Дождитесь завершения загрузки.
4. Получите файл прямо в Telegram!

Использование Telethon необходимо для обхода ограничения на размер файла для загрузки от имени бота (Чтобы грузить файлы более 50 мб)

## 📋 Особенности

- 🔍 Поддержка различных платформ (YouTube, Twitch, Instagram и др.).
- 🎞️ Выбор качества видео (до 1080p).
- 🎧 Возможность скачивания аудио в формате MP3.
- ⚡ Быстрая обработка запросов благодаря микросервисной архитектуре.

## 🛠️ Разработка

Проект следует структуре [golang-standards/project-layout](https://github.com/golang-standards/project-layout).

- `cmd/` - точки входа для приложений:
  - `bot/` - сервис бота на Python.
  - `downloader/` - сервис загрузки на Go.
- `internal/` - приватный код приложения:
  - `bot/` - обработчики команд, конфигурация и вспомогательные модули для бота.
  - `downloader/` - логика загрузки видео и аудио.
  - `pb/` - protobuf определения и сгенерированный код для gRPC.
  - `database/` - модели и взаимодействие с базой данных.
  - `utils/` - вспомогательные утилиты.

## 📜 Лицензия

Shield: [![CC BY-NC-SA 4.0][cc-by-nc-sa-shield]][cc-by-nc-sa]

This work is licensed under a
[Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License][cc-by-nc-sa].

[![CC BY-NC-SA 4.0][cc-by-nc-sa-image]][cc-by-nc-sa]

[cc-by-nc-sa]: http://creativecommons.org/licenses/by-nc-sa/4.0/
[cc-by-nc-sa-image]: https://licensebuttons.net/l/by-nc-sa/4.0/88x31.png
[cc-by-nc-sa-shield]: https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey.svg
