package main

import (
    "gopkg.in/yaml.v2"
    "io/ioutil"
    "log"
)

// Config 구조체는 설정 변수를 포함합니다.
type Config struct {
    Pubsub struct {
        DomainID         string `yaml:"domain_id"`
        ProjectID        string `yaml:"project_id"`
        TopicName        string `yaml:"topic_name"`
        CredentialID     string `yaml:"credential_id"`
        CredentialSecret string `yaml:"credential_secret"`
        SubscriptionName string `yaml:"sub_name"` 
    } `yaml:"pubsub"`
    SubscriptionName string `yaml:"subscription_name"`
}

// 전역 설정 변수
var config Config

func init() {
    // config.yml 파일을 읽어와서 config 구조체에 매핑
    configFile, err := ioutil.ReadFile("/home/ubuntu/syu-DataAnalyze/TrafficGenerator/config.yml")  // 절대 경로 사용
    if err != nil {
        log.Fatalf("Error reading config.yml: %v", err)
    }

    err = yaml.Unmarshal(configFile, &config)
    if err != nil {
        log.Fatalf("Error unmarshalling config.yml: %v", err)
    }

    // 읽어온 설정 값 출력 (디버깅용)
    log.Printf("DomainID: %s", config.Pubsub.DomainID)
    log.Printf("ProjectID: %s", config.Pubsub.ProjectID)
    log.Printf("TopicName: %s", config.Pubsub.TopicName)
    log.Printf("CredentialID: %s", config.Pubsub.CredentialID)
    log.Printf("CredentialSecret: %s", config.Pubsub.CredentialSecret)
    log.Printf("SubscriptionName: %s", config.Pubsub.SubscriptionName)
}
