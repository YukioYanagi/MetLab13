AGENT_CATALOG = [
    {
        "name": "SearchAvailabilityAgent",
        "subject": "hotel.rooms.search",
        "role": "Ищет свободные номера по городу, датам, количеству гостей и ценовому лимиту.",
        "input": ["city", "check_in", "check_out", "guests", "rooms", "max_price"],
        "output": ["status", "available_rooms", "agent_id", "handled_tasks"],
        "business_rules": [
            "Дата заезда должна быть раньше даты выезда.",
            "Срок проживания не должен превышать 30 ночей.",
            "Номер должен подходить по вместимости и бюджету.",
            "Занятые номера не попадают в результат.",
        ],
    },
    {
        "name": "BookingAgent",
        "subject": "hotel.bookings.create",
        "role": "Создаёт бронь на основании выбранного номера и данных гостя.",
        "input": ["room_id", "guest", "check_in", "check_out", "payment_hold_id"],
        "output": ["booking_id", "status", "total_amount"],
        "business_rules": [
            "Бронь возможна только для ранее найденного доступного номера.",
            "Должен быть заполнен профиль гостя.",
            "Перед подтверждением требуется успешный холд или оплата.",
        ],
    },
    {
        "name": "PaymentProcessingAgent",
        "subject": "hotel.payments.process",
        "role": "Проводит оплату или холд средств для бронирования.",
        "input": ["booking_id", "amount", "currency", "payment_method"],
        "output": ["payment_id", "status", "processed_at"],
        "business_rules": [
            "Сумма оплаты должна быть больше нуля.",
            "Валюта должна совпадать с валютой тарифа.",
            "При неуспешной оплате бронь не подтверждается.",
        ],
    },
    {
        "name": "CancellationManagementAgent",
        "subject": "hotel.bookings.cancel",
        "role": "Обрабатывает отмену брони и рассчитывает штраф или возврат.",
        "input": ["booking_id", "cancelled_at", "reason"],
        "output": ["status", "refund_amount", "penalty_amount"],
        "business_rules": [
            "Размер возврата зависит от дедлайна бесплатной отмены.",
            "Нельзя отменить уже заехавшую или завершённую бронь.",
            "После отмены должен быть освобождён номерной ресурс.",
        ],
    },
]
