package downloader

import (
	"context"
	"fmt"
	"log"
	"os"
	"os/exec"
	"path/filepath"
	"strconv"
	"strings"

	pb "Go_Yt_Downloader_bot/internal/pb/go"
)

// getPlatform определяет площадку по URL.
// Если URL содержит "twitch" или "youtube", возвращаются соответствующие значения,
// иначе возвращается "other" для всех остальных платформ (включая Instagram).
func getPlatform(url string) string {
    urlLower := strings.ToLower(url)
    if strings.Contains(urlLower, "twitch") {
        return "twitch"
    } else if strings.Contains(urlLower, "youtube") {
        return "youtube"
    }
    return "other"
}

// buildYtDlpArgs формирует список аргументов для yt-dlp в зависимости от платформы,
// типа медиа и параметра качества. Если платформа "youtube" или "twitch", добавляются
// флаги для указания качества. Для остальных платформ (включая Instagram и прочие)
// качество игнорируется – скачивается видео стандартным набором аргументов.
func buildYtDlpArgs(platform, mediaType, quality, outputFilename, url string) []string {
    args := []string{
        "--no-warnings",
        "--no-check-certificate",
        "--geo-bypass",
        "--force-overwrites",
        "--no-playlist",
    }

    if mediaType == "audio" {
        // Аргументы для аудио (одинаково для всех платформ).
        args = append(args, "-o", outputFilename, "-x", "--audio-format", "mp3", "--audio-quality", "0")
    } else if mediaType == "video" {
        // Основные параметры для видео.
        args = append(args, "--merge-output-format", "mp4", "-o", outputFilename)
        // Если платформа поддерживает выбор качества, добавляем соответствующие параметры.
        if platform == "youtube" {
            var height int
            if quality != "" {
                heightStr := strings.TrimSuffix(quality, "p")
                h, err := strconv.Atoi(heightStr)
                if err != nil {
                    log.Printf("Ошибка при преобразовании качества '%s' в число: %v. Используем качество по умолчанию.", quality, err)
                    height = 720
                } else {
                    height = h
                }
            } else {
                height = 720
            }

            if height > 1080 {
                height = 1080
            }

            var formatSpec string

            // Базовое предпочтение: точное совпадение + допуск ±100 + резерв по возрастанию
            formatSpec = fmt.Sprintf("bestvideo[ext=mp4][height=%d]+bestaudio/", height)
            formatSpec += fmt.Sprintf("bestvideo[ext=mp4][height<=%d][height>=%d]+bestaudio/", height+100, height-100)
            
            // Добавляем резервные качества по возрастанию
            resolutions := []int{144, 240, 360, 480, 720, 1080}
            for _, res := range resolutions {
                if height <= res {
                    formatSpec += fmt.Sprintf("bestvideo[ext=mp4][height<=%d]+bestaudio/best[height<=%d]/", res, res)
                }
            }
            
            // Убедимся, что всегда есть фоллбэк на лучшее доступное
            formatSpec += "bestvideo[ext=mp4]+bestaudio/best"
            
            args = append(args, "-f", formatSpec)
        }
    }
    // Добавляем URL в конец аргументов.
    args = append(args, url)
    return args
}

// DownloadVideo загружает видео с помощью yt-dlp без cookies.
// Качество применяется только для youtube; для всех остальных платформ
// скачивается видео стандартным набором параметров.
func (s *Service) DownloadVideo(ctx context.Context, req *pb.DownloadRequest) (*pb.DownloadResponse, error) {
    platform := getPlatform(req.Url)
    return s.download(ctx, req, "video", req.Quality, platform)
}

// DownloadAudio загружает аудио с помощью yt-dlp без cookies.
func (s *Service) DownloadAudio(ctx context.Context, req *pb.DownloadRequest) (*pb.DownloadResponse, error) {
    platform := getPlatform(req.Url)
    return s.download(ctx, req, "audio", "", platform)
}

// download загружает медиа с помощью yt-dlp, используя аргументы, сформированные функцией buildYtDlpArgs.
func (s *Service) download(ctx context.Context, req *pb.DownloadRequest, mediaType, quality, platform string) (*pb.DownloadResponse, error) {
    if req.Url == "" {
        return &pb.DownloadResponse{
            Error: "URL не указан",
        }, nil
    }

    if _, err := os.Stat(s.outputDir); os.IsNotExist(err) {
        if err := os.MkdirAll(s.outputDir, 0755); err != nil {
            return &pb.DownloadResponse{
                Error: fmt.Sprintf("Не удалось создать директорию вывода: %v", err),
            }, nil
        }
    }

    tempDir, err := os.MkdirTemp(s.outputDir, "yt_download_*")
    if err != nil {
        return nil, fmt.Errorf("ошибка при создании временной директории: %v", err)
    }

    log.Printf("Создана временная директория: %s", tempDir)

    outputFilename := filepath.Join(tempDir, "download")
    if mediaType == "audio" {
        outputFilename += ".mp3"
    } else {
        outputFilename += ".mp4"
    }

    log.Printf("Целевой файл: %s", outputFilename)

    args := buildYtDlpArgs(platform, mediaType, quality, outputFilename, req.Url)
    log.Printf("Команда скачивания: yt-dlp %s", strings.Join(args, " "))

    cmd := exec.CommandContext(ctx, "yt-dlp", args...)
    output, err := cmd.CombinedOutput()
    log.Printf("Вывод yt-dlp: %s", string(output))
    
    if err != nil {
        os.RemoveAll(tempDir)
        return &pb.DownloadResponse{
            Error: fmt.Sprintf("Ошибка при загрузке: %v\nВывод: %s", err, string(output)),
        }, nil
    }

    fileInfo, statErr := os.Stat(outputFilename)
    if statErr != nil {
        // Если файл не найден, пытаемся найти подходящий файл по расширению.
        log.Printf("Файл не найден: %s, ошибка: %v", outputFilename, statErr)
        for _, pattern := range []string{"*.mp4", "*.webm", "*.mkv", "*.mp4.*"} {
            if matches, _ := filepath.Glob(filepath.Join(tempDir, pattern)); len(matches) > 0 {
                log.Printf("Найден файл по расширению: %s", matches[0])
                return &pb.DownloadResponse{
                    FilePath: matches[0],
                }, nil
            }
        }
        os.RemoveAll(tempDir)
        return &pb.DownloadResponse{
            Error: fmt.Sprintf("Файл не был создан. Ошибка: %v\nВывод команды: %s", statErr, string(output)),
        }, nil
    }

    if fileInfo.Size() == 0 {
        log.Printf("Файл создан, но имеет нулевой размер: %s", outputFilename)
        os.RemoveAll(tempDir)
        return &pb.DownloadResponse{
            Error: "Файл был создан, но имеет нулевой размер",
        }, nil
    }

    log.Printf("Скачивание успешно! Размер файла: %d байт", fileInfo.Size())
    return &pb.DownloadResponse{
        FilePath: outputFilename,
        FileSize: fileInfo.Size(),
    }, nil
}

// Close освобождает ресурсы, удаляя временные директории.
func (s *Service) Close() error {
    files, err := filepath.Glob(filepath.Join(s.outputDir, "yt_download_*"))
    if err != nil {
        return err
    }
    for _, file := range files {
        os.RemoveAll(file)
    }
    return nil
}