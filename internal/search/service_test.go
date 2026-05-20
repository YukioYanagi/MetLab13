package search

import "testing"

func TestProcessReturnsAvailableRooms(t *testing.T) {
	service := NewService("agent-test-1", nil)

	response := service.Process(Request{
		RequestID: "req-101",
		City:      "Moscow",
		CheckIn:   "2026-06-12",
		CheckOut:  "2026-06-14",
		Guests:    2,
		Rooms:     1,
		MaxPrice:  150,
	})

	if response.Status != "success" {
		t.Fatalf("expected success status, got %s", response.Status)
	}
	if len(response.AvailableRooms) != 1 {
		t.Fatalf("expected 1 available room, got %d", len(response.AvailableRooms))
	}
	if response.AvailableRooms[0].RoomID != "aurora-std-101" {
		t.Fatalf("unexpected room returned: %s", response.AvailableRooms[0].RoomID)
	}
	if response.HandledTasks != 1 {
		t.Fatalf("expected handled task counter to be 1, got %d", response.HandledTasks)
	}
}

func TestProcessFiltersBlockedRoomsAndPrice(t *testing.T) {
	service := NewService("agent-test-2", nil)

	response := service.Process(Request{
		RequestID: "req-102",
		City:      "Moscow",
		CheckIn:   "2026-06-10",
		CheckOut:  "2026-06-12",
		Guests:    2,
		Rooms:     1,
		MaxPrice:  150,
	})

	if response.Status != "success" {
		t.Fatalf("expected success status, got %s", response.Status)
	}
	if len(response.AvailableRooms) != 0 {
		t.Fatalf("expected 0 available rooms, got %d", len(response.AvailableRooms))
	}
}

func TestProcessRejectsInvalidDates(t *testing.T) {
	service := NewService("agent-test-3", nil)

	response := service.Process(Request{
		RequestID: "req-103",
		City:      "Moscow",
		CheckIn:   "2026-06-15",
		CheckOut:  "2026-06-14",
		Guests:    2,
		Rooms:     1,
	})

	if response.Status != "error" {
		t.Fatalf("expected error status, got %s", response.Status)
	}
	if response.Message != "check_in must be earlier than check_out" {
		t.Fatalf("unexpected validation error: %s", response.Message)
	}
	if response.HandledTasks != 1 {
		t.Fatalf("expected handled task counter to be 1, got %d", response.HandledTasks)
	}
}

func TestProcessChecksRequestedRoomCount(t *testing.T) {
	service := NewService("agent-test-4", nil)

	response := service.Process(Request{
		RequestID: "req-104",
		City:      "Moscow",
		CheckIn:   "2026-06-12",
		CheckOut:  "2026-06-14",
		Guests:    2,
		Rooms:     2,
		MaxPrice:  150,
	})

	if response.Status != "success" {
		t.Fatalf("expected success status, got %s", response.Status)
	}
	if len(response.AvailableRooms) != 0 {
		t.Fatalf("expected 0 available rooms when room count is insufficient, got %d", len(response.AvailableRooms))
	}
	if response.Message != "not enough rooms available for requested room count" {
		t.Fatalf("unexpected message: %s", response.Message)
	}
}
