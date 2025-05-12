package main

import (
	"log"
	"net"
	"os"

	"Go_Yt_Downloader_bot/internal/downloader"
	pb "Go_Yt_Downloader_bot/internal/pb/go"

	"github.com/joho/godotenv"
	"google.golang.org/grpc"
)

func main() {
	// Загружаем переменные из .env файла
	if err := godotenv.Load(); err != nil {
		log.Println("Файл .env не найден, используем переменные окружения системы")
	}

	port := os.Getenv("PORT_DOWNLOADER")
	if port == "" {
		port = "50051"
	}

	lis, err := net.Listen("tcp", ":"+port)
	if err != nil {
		log.Fatalf("Failed to listen: %v", err)
	}

	server := grpc.NewServer()
	service, err := downloader.NewService(os.Getenv("OUTPUT_DIR"))
	if err != nil {
		log.Fatalf("Failed to create downloader service: %v", err)
	}
	pb.RegisterDownloaderServer(server, service)

	log.Printf("Downloader service is running on port %s", port)
	if err := server.Serve(lis); err != nil {
		log.Fatalf("Failed to serve: %v", err)
	}
}
