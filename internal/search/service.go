package search

import (
	"fmt"
	"log"
	"strings"
	"sync/atomic"
	"time"
)

const dateLayout = "2006-01-02"

type Service struct {
	agentID string
	logger  *log.Logger
	counter atomic.Uint64
}

func NewService(agentID string, logger *log.Logger) *Service {
	return &Service{
		agentID: agentID,
		logger:  logger,
	}
}

func (s *Service) Process(request Request) Response {
	handled := s.NextHandledCount()

	if err := validate(request); err != nil {
		if s.logger != nil {
			s.logger.Printf("ERROR validation failed request_id=%s error=%v", request.RequestID, err)
		}

		return ErrorResponse(s.agentID, request.RequestID, err.Error(), handled)
	}

	checkIn, _ := time.Parse(dateLayout, request.CheckIn)
	checkOut, _ := time.Parse(dateLayout, request.CheckOut)

	rooms := make([]RoomOffer, 0)
	for _, candidate := range roomCatalog {
		if !strings.EqualFold(candidate.Room.City, request.City) {
			continue
		}
		if candidate.Room.Capacity < request.Guests {
			continue
		}
		if request.MaxPrice > 0 && candidate.Room.PricePerNight > request.MaxPrice {
			continue
		}
		if isRoomBlocked(candidate.BlockedRanges, checkIn, checkOut) {
			continue
		}

		rooms = append(rooms, candidate.Room)
	}

	message := "available rooms found"
	if len(rooms) == 0 {
		message = "no rooms available for selected dates"
	} else if len(rooms) < request.Rooms {
		message = "not enough rooms available for requested room count"
		rooms = []RoomOffer{}
	} else if len(rooms) > request.Rooms {
		rooms = rooms[:request.Rooms]
	}

	return Response{
		RequestID:      request.RequestID,
		Status:         "success",
		AgentID:        s.agentID,
		Message:        message,
		AvailableRooms: rooms,
		HandledTasks:   handled,
	}
}

func (s *Service) NextHandledCount() uint64 {
	return s.counter.Add(1)
}

func ErrorResponse(agentID, requestID, message string, handled uint64) Response {
	return Response{
		RequestID:      requestID,
		Status:         "error",
		AgentID:        agentID,
		Message:        message,
		AvailableRooms: []RoomOffer{},
		HandledTasks:   handled,
	}
}

func validate(request Request) error {
	if strings.TrimSpace(request.RequestID) == "" {
		return fmt.Errorf("request_id is required")
	}
	if strings.TrimSpace(request.City) == "" {
		return fmt.Errorf("city is required")
	}
	if request.Guests <= 0 {
		return fmt.Errorf("guests must be greater than zero")
	}
	if request.Rooms <= 0 {
		return fmt.Errorf("rooms must be greater than zero")
	}
	if request.MaxPrice < 0 {
		return fmt.Errorf("max_price must not be negative")
	}

	checkIn, err := time.Parse(dateLayout, request.CheckIn)
	if err != nil {
		return fmt.Errorf("check_in must be in YYYY-MM-DD format")
	}
	checkOut, err := time.Parse(dateLayout, request.CheckOut)
	if err != nil {
		return fmt.Errorf("check_out must be in YYYY-MM-DD format")
	}
	if !checkIn.Before(checkOut) {
		return fmt.Errorf("check_in must be earlier than check_out")
	}
	if checkOut.Sub(checkIn) > 30*24*time.Hour {
		return fmt.Errorf("stay must not exceed 30 nights")
	}

	return nil
}

func isRoomBlocked(blockedRanges []DateRange, checkIn, checkOut time.Time) bool {
	for _, blocked := range blockedRanges {
		blockedFrom, err := time.Parse(dateLayout, blocked.From)
		if err != nil {
			continue
		}
		blockedTo, err := time.Parse(dateLayout, blocked.To)
		if err != nil {
			continue
		}

		if checkIn.Before(blockedTo) && blockedFrom.Before(checkOut) {
			return true
		}
	}
	return false
}
