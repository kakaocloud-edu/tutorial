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
    configFile, err := ioutil.ReadFile("/home/ubuntu/DataAnalyzeCourse/src/day1/Lab01/traffic_generator/config.yml")  // 절대 경로 사용
    if err != nil {
        log.Fatalf("Error reading config.yml: %v", err)
    }

    err = yaml.Unmarshal(configFile, &config)
    if err != nil {
        log.Fatalf("Error unmarshalling config.yml: %v", err)
    }
}
