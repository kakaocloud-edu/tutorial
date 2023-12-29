# ConfigMap 

지금까지 만든 배포 방식을 자동화하는 도구인 Helm에 대해 실습합니다. Helm을 이용해 Chart를 만들어 배포, 업데이트, 롤백을 진행하는 실습입니다.


## 1. yaml 파일을 이용해 배포된 내용 수정하기

1. lab6-ConfigMap.yaml 파일 수정
   - 터미널에 아래 명령어를 입력하세요.
   #### **lab6-4-1**
   ```bash
   sudo vi lab6-ConfigMap.yaml
   ```

2. `WelCome_MESSAGE` 내용을 변경해 웹 사이트 문구 변경하기

   **Note** 아래와 같은 방식으로 문구를 변경하면 됩니다.
   #### **lab6-4-2**
   ```bash
   apiVersion: v1
   kind: ConfigMap
   metadata:
      name: app-config
   data:
      WELCOME_MESSAGE: "ConfigMap변경 실습"
      BACKGROUND_COLOR: "#4a69bd"
   ```

3. 수정된 yaml 파일 적용
   #### **lab6-4-3**
   ```bash
   kubectl apply -f ./lab6-ConfigMap.yaml
   ```

4. Pod최신화를 위해 기존 리소스(Pod)제거
   #### **lab6-4-4**
   ```bash
   kubectl delete pod —-all
   ```

5. 웹 사이트에 재접속해서 변경한 문구가 적용되었는지 확인하기
   
