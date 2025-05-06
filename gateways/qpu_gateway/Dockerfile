# syntax=docker/dockerfile:1.6
FROM golang:1.22-bookworm AS builder
WORKDIR /src
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -o /bin/qpu-gateway main.go

FROM gcr.io/distroless/static:nonroot
COPY --from=builder /bin/qpu-gateway /qpu-gateway
ENTRYPOINT ["/qpu-gateway"]
