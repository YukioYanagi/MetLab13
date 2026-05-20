package search

type Request struct {
	RequestID string  `json:"request_id"`
	City      string  `json:"city"`
	CheckIn   string  `json:"check_in"`
	CheckOut  string  `json:"check_out"`
	Guests    int     `json:"guests"`
	Rooms     int     `json:"rooms"`
	MaxPrice  float64 `json:"max_price,omitempty"`
}

type Response struct {
	RequestID      string      `json:"request_id"`
	Status         string      `json:"status"`
	AgentID        string      `json:"agent_id"`
	Message        string      `json:"message"`
	AvailableRooms []RoomOffer `json:"available_rooms"`
	HandledTasks   uint64      `json:"handled_tasks"`
}

type RoomOffer struct {
	HotelID        string   `json:"hotel_id"`
	HotelName      string   `json:"hotel_name"`
	City           string   `json:"city"`
	RoomID         string   `json:"room_id"`
	RoomType       string   `json:"room_type"`
	Capacity       int      `json:"capacity"`
	PricePerNight  float64  `json:"price_per_night"`
	Currency       string   `json:"currency"`
	Amenities      []string `json:"amenities"`
	CancellationTo string   `json:"cancellation_to"`
}

type DateRange struct {
	From string `json:"from"`
	To   string `json:"to"`
}

type roomInventory struct {
	Room          RoomOffer
	BlockedRanges []DateRange
}
