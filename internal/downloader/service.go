package downloader

import (
	"fmt"
	"os"
	"os/exec"

	pb "Go_Yt_Downloader_bot/internal/pb/go"
)

// Service представляет сервис загрузки видео
type Service struct {
	pb.UnimplementedDownloaderServer
	outputDir string
	downloads map[string]*Download
}

// Download представляет информацию о загрузке
type Download struct {
	FilePath        string
	Error           string
	FileSize	    int64
}

// NewService создает новый сервис загрузки
func NewService(outputDir string) (*Service, error) {
	_, err := exec.LookPath("yt-dlp")
	if err != nil {
		return nil, fmt.Errorf("yt-dlp не найден в системе: %v", err)
	}

	if err := os.MkdirAll(outputDir, 0755); err != nil {
		return nil, fmt.Errorf("ошибка при создании директории для загрузок: %v", err)
	}

	return &Service{
		outputDir: outputDir,
		downloads: make(map[string]*Download),
	}, nil
}
