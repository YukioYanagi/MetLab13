package search

var roomCatalog = []roomInventory{
	{
		Room: RoomOffer{
			HotelID:        "hotel-aurora",
			HotelName:      "Aurora Riverside",
			City:           "Moscow",
			RoomID:         "aurora-std-101",
			RoomType:       "Standard",
			Capacity:       2,
			PricePerNight:  120,
			Currency:       "USD",
			Amenities:      []string{"Wi-Fi", "Breakfast", "Work desk"},
			CancellationTo: "2026-06-10T18:00:00Z",
		},
		BlockedRanges: []DateRange{
			{From: "2026-06-10", To: "2026-06-12"},
			{From: "2026-06-20", To: "2026-06-22"},
		},
	},
	{
		Room: RoomOffer{
			HotelID:        "hotel-aurora",
			HotelName:      "Aurora Riverside",
			City:           "Moscow",
			RoomID:         "aurora-deluxe-305",
			RoomType:       "Deluxe",
			Capacity:       3,
			PricePerNight:  180,
			Currency:       "USD",
			Amenities:      []string{"Wi-Fi", "Breakfast", "Balcony"},
			CancellationTo: "2026-06-10T18:00:00Z",
		},
	},
	{
		Room: RoomOffer{
			HotelID:        "hotel-neva",
			HotelName:      "Grand Neva",
			City:           "Saint Petersburg",
			RoomID:         "neva-suite-501",
			RoomType:       "Suite",
			Capacity:       4,
			PricePerNight:  250,
			Currency:       "USD",
			Amenities:      []string{"Wi-Fi", "Breakfast", "River view"},
			CancellationTo: "2026-06-09T18:00:00Z",
		},
		BlockedRanges: []DateRange{
			{From: "2026-06-14", To: "2026-06-18"},
		},
	},
	{
		Room: RoomOffer{
			HotelID:        "hotel-cedar",
			HotelName:      "Cedar Garden",
			City:           "Kazan",
			RoomID:         "cedar-family-210",
			RoomType:       "Family",
			Capacity:       4,
			PricePerNight:  160,
			Currency:       "USD",
			Amenities:      []string{"Wi-Fi", "Breakfast", "Kids zone"},
			CancellationTo: "2026-06-08T18:00:00Z",
		},
	},
}
