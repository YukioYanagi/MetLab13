Долгополов Андрей Дмитриевич, группа 221331, Лабораторная работа 12. Вариант 6

# Multi-Agent Hotel Booking System

Учебный проект по теме бронирования гостиниц, в котором предметная область разложена на несколько типов агентов:

- агент поиска свободных номеров;
- агент бронирования;
- агент обработки оплаты;
- агент управления отменами.

В коде реализован полноценный исполняемый прототип для `SearchAvailabilityAgent` на Go, а остальные агенты описаны архитектурно и подготовлены как расширение системы. Это соответствует формулировке задания, где требуется реализовать одного рабочего агента, но адаптировать всю систему под предметную область.

## Что покрыто по 10 заданиям

1. Определение агентов и ролей: `docs/architecture.md`
2. Go-агент: `cmd/search-agent/main.go`
3. Python-оркестратор: `orchestrator/service.py`
4. Коммуникация через NATS и Docker Compose: `docker-compose.yml`
5. Логирование и мониторинг: `internal/platform/logger.go`, `orchestrator/logging_config.py`
6. Retry и timeout: `orchestrator/service.py`
7. Несколько агентов одного типа и балансировка: `docker compose up --build --scale search-agent=3`, `orchestrator/demo.py`
8. REST API на FastAPI: `api/main.py`
9. Тесты: `internal/search/service_test.go`, `tests/test_orchestrator.py`
10. Архитектура и диаграммы: `docs/architecture.md`

## Структура проекта

```text
.
├── api/                     # FastAPI HTTP API
├── cmd/search-agent/        # Точка входа Go-агента
├── docker/                  # Dockerfile для Python API и Go-агента
├── docs/                    # Архитектурная документация и диаграммы
├── examples/                # Примеры JSON-задач
├── internal/                # Go-домен, логика, логирование
├── orchestrator/            # Python-оркестратор и demo-сценарий
└── tests/                   # Тесты Python-оркестратора
```

## Быстрый запуск через Docker

```powershell
docker compose up --build --scale search-agent=3
```

После запуска:

- NATS будет доступен на `nats://localhost:4222`
- FastAPI будет доступен на `http://localhost:8000`
- метрики API: `http://localhost:8000/metrics`

Пример HTTP-запроса:

```powershell
$body = @{
  city = "Moscow"
  check_in = "2026-06-12"
  check_out = "2026-06-14"
  guests = 2
  rooms = 1
  max_price = 220
} | ConvertTo-Json

Invoke-RestMethod `
  -Method Post `
  -Uri "http://localhost:8000/search" `
  -ContentType "application/json" `
  -Body $body
```

## Локальный запуск без Docker

### 1. Поднять NATS

```powershell
docker compose up nats
```

### 2. Установить Python-зависимости

```powershell
python -m pip install -r requirements.txt
```

### 3. Подтянуть Go-зависимости

```powershell
go mod tidy
```

### 4. Запустить Go-агента

```powershell
go run ./cmd/search-agent
```

### 5. Запустить API

```powershell
uvicorn api.main:app --host 0.0.0.0 --port 8000
```

## Демонстрация балансировки нагрузки

Если поднято несколько экземпляров `search-agent`, можно отправить пачку задач и увидеть, что в ответах меняется `agent_id`:

```powershell
python -m orchestrator.demo
```

Сценарий отправляет несколько запросов параллельно и в конце печатает распределение задач по агентам.

## Тесты

Go:

```powershell
go test ./internal/search -v
```

Python:

```powershell
pytest tests/test_orchestrator.py -q
```

## Логи

Логи пишутся и в консоль, и в папку `logs/`:

- `logs/api.log`
- `logs/orchestrator.log`
- `logs/search-agent-<agent_id>.log`

## Основные NATS subject-ы

- `hotel.rooms.search`
- `hotel.bookings.create`
- `hotel.payments.process`
- `hotel.bookings.cancel`

## Примечание

Исполняемый агент в этом проекте один: `SearchAvailabilityAgent`. Остальные типы агентов полностью описаны в архитектуре и могут быть добавлены по тому же шаблону без изменения общей схемы оркестрации.
