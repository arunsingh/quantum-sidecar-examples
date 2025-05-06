package main

/* there is qpu_gateway/proto/quantum.proto file, generate proto via bash
$ protoc --go_out=. --go-grpc_out=. quantum.proto

*/

import (
  "context"
  "crypto/tls"
  "log"
  "net"
  "os"
  "time"

  qpb "github.com/arunsingh/quantum-sidecar-examples/gateways/qpu_gateway/proto"
  "github.com/go-redis/redis/v8"
  "google.golang.org/grpc"
  "google.golang.org/grpc/credentials"
)

type server struct {
  qpb.UnimplementedQuantumServiceServer
  rdb *redis.Client
}

func (s *server) RunQuil(req *qpb.RunQuilRequest, stream qpb.QuantumService_RunQuilServer) error {
  key := hash(req)
  ctx := stream.Context()
  if val, err := s.rdb.Get(ctx, key).Result(); err == nil {
    return stream.Send(&qpb.QuilResult{Ro: []int32{}}) // send cached (simplified)
  }
  // call Rigetti REST
  ro := []int32{1, 0, 1} // placeholder
  s.rdb.Set(ctx, key, ro, 24*time.Hour)
  return stream.Send(&qpb.QuilResult{Ro: ro})
}

func main() {
  port := "50051"
  lis, err := net.Listen("tcp", ":"+port)
  if err != nil { log.Fatal(err) }

  tlsConfig := &tls.Config{MinVersion: tls.VersionTLS13}
  grpcSrv := grpc.NewServer(grpc.Creds(credentials.NewTLS(tlsConfig)))

  rdb := redis.NewClient(&redis.Options{Addr: "localhost:6379"})
  qpb.RegisterQuantumServiceServer(grpcSrv, &server{rdb: rdb})

  log.Printf("gRPC QPU gateway on %s", port)
  if err := grpcSrv.Serve(lis); err != nil { log.Fatal(err) }
}
