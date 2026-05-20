package main

import (
	"context"
	"encoding/json"
	"os"
	"os/signal"
	"syscall"
	"time"

	"github.com/nats-io/nats.go"

	"metlab13/internal/platform"
	"metlab13/internal/search"
)

func main() {
	agentID := envOr("AGENT_ID", platform.HostnameOr("search-agent"))
	logDir := envOr("LOG_DIR", "logs")
	logLevel := envOr("LOG_LEVEL", "INFO")
	natsURL := envOr("NATS_URL", "nats://localhost:4222")
	searchSubject := envOr("SEARCH_SUBJECT", "hotel.rooms.search")
	searchQueue := envOr("SEARCH_QUEUE", "hotel-search-workers")
	resultSubject := envOr("RESULT_SUBJECT", "hotel.rooms.search.result")

	logger, err := platform.NewLogger("search-agent", agentID, logDir)
	if err != nil {
		panic(err)
	}

	logger.Printf("INFO agent starting agent_id=%s log_level=%s nats_url=%s subject=%s queue=%s", agentID, logLevel, natsURL, searchSubject, searchQueue)

	nc, err := nats.Connect(
		natsURL,
		nats.Name("search-agent-"+agentID),
		nats.RetryOnFailedConnect(true),
		nats.MaxReconnects(-1),
		nats.ReconnectWait(2*time.Second),
	)
	if err != nil {
		logger.Printf("ERROR failed to connect to NATS: %v", err)
		os.Exit(1)
	}
	defer nc.Close()

	service := search.NewService(agentID, logger)

	_, err = nc.QueueSubscribe(searchSubject, searchQueue, func(msg *nats.Msg) {
		var request search.Request
		if err := json.Unmarshal(msg.Data, &request); err != nil {
			logger.Printf("ERROR invalid JSON payload: %v", err)
			response := search.ErrorResponse(agentID, "invalid-json", "payload is not valid JSON", service.NextHandledCount())
			publishResponse(nc, logger, msg, resultSubject, response)
			return
		}

		response := service.Process(request)
		publishResponse(nc, logger, msg, resultSubject, response)

		logger.Printf(
			"INFO task processed request_id=%s status=%s rooms=%d handled_tasks=%d",
			response.RequestID,
			response.Status,
			len(response.AvailableRooms),
			response.HandledTasks,
		)
	})
	if err != nil {
		logger.Printf("ERROR failed to subscribe: %v", err)
		os.Exit(1)
	}

	if err := nc.Flush(); err != nil {
		logger.Printf("ERROR failed to flush NATS connection: %v", err)
		os.Exit(1)
	}

	ctx, stop := signal.NotifyContext(context.Background(), os.Interrupt, syscall.SIGTERM)
	defer stop()
	<-ctx.Done()

	logger.Printf("INFO shutdown signal received")
}

func publishResponse(nc *nats.Conn, logger *platform.Logger, msg *nats.Msg, fallbackSubject string, response search.Response) {
	payload, err := json.Marshal(response)
	if err != nil {
		logger.Printf("ERROR failed to marshal response: %v", err)
		return
	}

	target := msg.Reply
	if target == "" {
		target = fallbackSubject
	}

	if target == "" {
		logger.Printf("ERROR missing reply subject and fallback subject")
		return
	}

	if err := nc.Publish(target, payload); err != nil {
		logger.Printf("ERROR failed to publish response: %v", err)
	}
}

func envOr(key, fallback string) string {
	value := os.Getenv(key)
	if value == "" {
		return fallback
	}
	return value
}
