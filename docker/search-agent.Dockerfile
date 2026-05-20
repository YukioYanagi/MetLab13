FROM golang:1.26-alpine AS builder

WORKDIR /src

COPY go.mod go.sum ./
RUN go mod download

COPY cmd ./cmd
COPY internal ./internal

RUN CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build -o /out/search-agent ./cmd/search-agent

FROM alpine:3.22

WORKDIR /app

RUN mkdir -p /app/logs
COPY --from=builder /out/search-agent /usr/local/bin/search-agent

CMD ["search-agent"]
