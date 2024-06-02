# AutoML 실험 및 Kubernetes 리소스 모니터링
AutoML 실험을 생성하고, 해당 실험과 관련된 Kubernetes 리소스(Experiment, Suggestion, Trial, Job, Pod)를 관측하는 실습입니다.

## 1. AutoML 실험 생성
1. bastion VM 터미널에서 Experiment.yaml 파일 내용 복사
- **Note**: 아래 명령어를 입력한 뒤 출력된 파일 내용을 복사하세요.
    #### **lab7-1-3**
    ```bash
    apiVersion: "kubeflow.org/v1beta1"
    kind: Experiment
    metadata:
      name: mnist-hyperparameter-tuning
      namespace: kubeflow
    spec:
      objective:
        type: maximize
        goal: 0.99
        objectiveMetricName: accuracy
        additionalMetricNames:
          - loss
      algorithm:
        algorithmName: random
      parallelTrialCount: 10
      maxTrialCount: 12
      maxFailedTrialCount: 3
      parameters:
        - name: --learning_rate
          parameterType: double
          feasibleSpace:
            min: "0.0001"
            max: "0.01"
        - name: --batch_size
          parameterType: int
          feasibleSpace:
            min: "16"
            max: "128"
      trialTemplate:
        retain: true
        primaryContainerName: mnist-training
        trialParameters:
          - name: learningRate
            description: Learning rate for the model
            reference: --learning_rate
          - name: batchSize
            description: Batch size for the model
            reference: --batch_size
        trialSpec:
          apiVersion: batch/v1
          kind: Job
          spec:
            template:
              metadata:
                annotations:
                  sidecar.istio.io/inject: 'false'
              spec:
                containers:
                  - name: mnist-training
                    image: ${PROJECT_NAME}.kr-central-2.kcr.dev/kakao-registry/hyperpram
                    command:
                      - "python"
                      - "mnist_train.py"
                      - "--learning_rate=${trialParameters.learningRate}"
                      - "--batch_size=${trialParameters.batchSize}"
                restartPolicy: Never
                imagePullSecrets:
                  - name: regcred
      metricsCollectorSpec:
        source:
          filter:
            metricsFormat:
              - "{metricName: ([\\w|-]+), metricValue: ((-?\\d+)(\\.\\d+)?)}"
          fileSystemPath:
            path: "/tmp/mnist.log"
            kind: File
        collector:
          kind: File
    ```
2. Kubeflow 대시보드의 Experiments (AutoML) 탭 > [New Experiment] 버튼 클릭
3. 하단의 Edit 클릭
4. 기존 내용을 지운 뒤 터미널에서 복사한 Experiment.yaml 내용을 복사여 붙여넣고 [CREATE] 버튼 클릭

## 2. AutoML 실험 결과 확인
1. 생성된 mnist-hyperparameter-tuning 클릭
2. OVERVIEW 탭 확인
3. TRIALS 탭 확인
4. DETAILS 탭 확인

## 3. 리소스 모니터링
- **Note**: bastion VM 접속 터미널 창에 아래 명령어들을 입력하세요.
1. Experiment 생성함
    #### **lab7-3-1**
    ```
    kubectl get Experiment -n kbm-u-kubeflow-tutorial
    ```
2. Experiment Controller가 Suggestion을 생성함
    #### **lab7-3-2**
    ```
    kubectl get Suggestion -n kbm-u-kubeflow-tutorial
    ```
3. Trial Controller가 Suggestion에 작성된 하이퍼파라미터 설정을 기반으로 Trial들을 생성 > Trial들이 Job을 생성 > Job이 Pod들을 생성함
    #### **lab7-3-3-1**
    - **Note**: 현재 네임스페이스에서 실행 중인 Trial 목록 확인
    - **Note**: Trial - 제안된 하이퍼파라미터 설정에 따라 생성된 실험 실행 단위
    ```
    kubectl get trials -n kbm-u-kubeflow-tutorial
    ```

    #### **lab7-3-3-2**
    - **Note**: 현재 네임스페이스에서 실행 중인 Job 목록 확인
    - **Note**: Job - 각 Trial에서 수행되는 작업으로, 실제 모델 학습 등의 작업 처리
    ```
    kubectl get trials -n kbm-u-kubeflow-tutorial
    ```

   #### **lab7-3-3-2**
   - **Note**: 현재 네임스페이스에서 실행 중인 Pod 목록 확인
   - **Note**: Pod - Job에 의해 생성된 컨테이너 단위로, 실제 컴퓨팅 리소스를 사용하여 작업 수행
   ```
   kubectl get job -n kbm-u-kubeflow-tutorial
   ```
