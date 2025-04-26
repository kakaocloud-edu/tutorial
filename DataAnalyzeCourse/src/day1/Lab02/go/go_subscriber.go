package main

import (
    "context"
    "encoding/base64"
    "fmt"
    "log"
    "os"
    "os/signal"
    "syscall"

    "github.kakaoenterprise.in/cloud-platform/kc-pub-sub-sdk-go"
    "github.kakaoenterprise.in/cloud-platform/kc-pub-sub-sdk-go/option"
)

func main() {
    // 환경 설정
    domainID := config.Pubsub.DomainID        // config.Pubsub.DomainID로 변경
    projectID := config.Pubsub.ProjectID      // config.Pubsub.ProjectID로 변경
    subscriptionName := config.Pubsub.SubscriptionName // config.Pubsub.SubscriptionName으로 변경
    credentialID := config.Pubsub.CredentialID // config.Pubsub.CredentialID로 변경
    credentialSecret := config.Pubsub.CredentialSecret // config.Pubsub.CredentialSecret으로 변경

    // 클라이언트 초기화
    ctx, cancel := context.WithCancel(context.Background())
    defer cancel()

    accessKey := pubsub.AccessKey{
        CredentialID:     credentialID,
        CredentialSecret: credentialSecret,
    }

    opts := []option.ClientOption{
        option.WithAccessKey(accessKey),
    }

    client, err := pubsub.NewClient(ctx, domainID, projectID, opts...)
    if err != nil {
        log.Fatalf("Pub/Sub 클라이언트 생성 실패: %v", err)
    }
    defer func() {
        if err := client.Close(); err != nil {
            log.Printf("클라이언트 종료 중 오류: %v", err)
        }
    }()

    // 서브스크립션 객체 가져오기
    subscription := client.Subscription(subscriptionName)
    subscription.ReceiveSettings.NumGoroutines = 5

    // Graceful shutdown 처리
    go func() {
        stopChan := make(chan os.Signal, 1)
        signal.Notify(stopChan, os.Interrupt, syscall.SIGTERM)
        <-stopChan
        fmt.Println("\n프로그램 종료 요청 수신. 메시지 수신을 중단합니다...")
        cancel()
    }()

    // 메시지 수신
    fmt.Println("메시지 수신을 시작합니다...")
    err = subscription.Receive(ctx, func(ctx2 context.Context, message *pubsub.Message) {
        data, err := base64.StdEncoding.DecodeString(message.Data)
        if err != nil {
            log.Printf("메시지 디코딩 오류: %v", err)
            message.Nack()
            return
        }

        log.Printf("수신된 메시지 ID: %s\n", message.ID)
        log.Printf("내용: %s\n", string(data))
        message.Ack()
    })

    if err != nil {
        log.Printf("메시지 수신 오류: %v", err)
    }
}
