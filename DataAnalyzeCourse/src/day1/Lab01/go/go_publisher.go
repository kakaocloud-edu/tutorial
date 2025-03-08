package main

import (
    "bufio"
    "context"
    "encoding/base64"
    "fmt"
    "log"
    "os"
    "strings"

    "github.kakaoenterprise.in/cloud-platform/kc-pub-sub-sdk-go"
    "github.kakaoenterprise.in/cloud-platform/kc-pub-sub-sdk-go/option"
)

func main() {
    // 환경 설정
    domainID := config.Pubsub.DomainID       // config.Pubsub.DomainID로 변경
    projectID := config.Pubsub.ProjectID     // config.Pubsub.ProjectID로 변경
    topicName := config.Pubsub.TopicName     // config.Pubsub.TopicName으로 변경
    credentialID := config.Pubsub.CredentialID // config.Pubsub.CredentialID로 변경
    credentialSecret := config.Pubsub.CredentialSecret // config.Pubsub.CredentialSecret으로 변경

    // 액세스 키 생성 (확인용 로그 추가)
    log.Printf("Using CredentialID: %s, CredentialSecret: %s", credentialID, credentialSecret)

    accessKey := pubsub.AccessKey{
        CredentialID:     credentialID,
        CredentialSecret: credentialSecret,
    }

    // 클라이언트 초기화
    ctx := context.Background()
    opts := []option.ClientOption{
        option.WithAccessKey(accessKey), // 액세스 키를 옵션에 추가
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

    // 토픽 가져오기
    topic := client.Topic(topicName)

    // 메시지 입력 처리
    scanner := bufio.NewScanner(os.Stdin)
    fmt.Println("메시지를 입력하세요. 종료하려면 'exit'를 입력하세요.")

    for {
        fmt.Print("메시지: ")
        if !scanner.Scan() {
            break
        }
        text := strings.TrimSpace(scanner.Text())
        if strings.ToLower(text) == "exit" {
            fmt.Println("프로그램을 종료합니다.")
            break
        }

        if text == "" {
            fmt.Println("빈 메시지는 게시할 수 없습니다.")
            continue
        }

        // 메시지 속성 정의
        attributes := map[string]string{
            "source": "go_sdk_publisher",
            "level":  "info",
        }

        // 메시지 생성
        msg := &pubsub.Message{
            Data:       base64.StdEncoding.EncodeToString([]byte(text)),
            Attributes: attributes,
        }

        // 메시지 게시
        result := topic.Publish(ctx, msg)
        id, err := result.Get(ctx)
        if err != nil {
            log.Printf("메시지 게시 실패: %v\n", err)
        } else {
            fmt.Printf("메시지가 게시되었습니다. 메시지 ID: %s\n", id)
        }
    }

    if err := scanner.Err(); err != nil {
        log.Fatalf("입력 처리 중 오류 발생: %v", err)
    }
}
