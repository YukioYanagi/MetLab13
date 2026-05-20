package platform

import (
	"io"
	"log"
	"os"
	"path/filepath"
	"strings"
)

type Logger = log.Logger

func NewLogger(serviceName, agentID, logDir string) (*Logger, error) {
	if err := os.MkdirAll(logDir, 0o755); err != nil {
		return nil, err
	}

	fileName := serviceName
	if agentID != "" {
		fileName += "-" + sanitizeFileName(agentID)
	}
	filePath := filepath.Join(logDir, fileName+".log")

	file, err := os.OpenFile(filePath, os.O_CREATE|os.O_WRONLY|os.O_APPEND, 0o644)
	if err != nil {
		return nil, err
	}

	writer := io.MultiWriter(os.Stdout, file)
	logger := log.New(writer, "", log.LstdFlags|log.LUTC)
	return logger, nil
}

func HostnameOr(fallback string) string {
	host, err := os.Hostname()
	if err != nil || host == "" {
		return fallback
	}
	return host
}

func sanitizeFileName(value string) string {
	replacer := strings.NewReplacer("\\", "-", "/", "-", ":", "-", " ", "-")
	return replacer.Replace(value)
}
