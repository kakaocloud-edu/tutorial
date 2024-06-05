# 간단한 Notebook 실습
CPU, GPU Notebook을 각각 생성하고 Tensorboard, 하이퍼파라미터 튜닝 등을 실습합니다.

## 1. GPU 기반 Jupyter Notebook 생성
1. kbm-u-Kubeflow-tutorial 네임스페이스 선택 > 좌측 메뉴바의 Notebooks 탭 클릭
2. `+ New Notebook` 클릭
   - 노트북 설정
     - Name : `gpu-notebook`
     - Namespace : `kbm-u-Kubeflow-tutorial`
     - Image : `mlops-pipelines/jupyter- tensorflow-full:v1.0.1.py36`
     - Requested CPUs : `2`
     - Requested memory in Gi : `8`
     - Number of GPUs : `4` 
     - GPU Vendor : `NVIDIA MIC - 1g.10gb`  
     - Volume / Configurations 설정 : `모두 기존 값 사용`
     - Affinity : `pool-gpu`
     - Tolerations : `None(기존 값)`
     - Miscellaneous Settings :  `기존 값 사용`
3. `Launch` 클릭
4. Notebook 생성 확인

## 2. .ipynb 파일 업로드
1. Notebooks 탭 > `cpu-notebook`의 `CONNECT` 클릭
2. Other 중 `Terminal` 클릭
3. TensorFlow 라이브러리 cpu-notebook에 설치
   #### **Lab5-2-3**
   ```bash
   pip install tensorflow
   ```

4. kubectl.ipynb 파일 다운로드
   #### **Lab5-2-4**
   ```bash
   wget https://github.com/kakaocloud-edu/tutorial/raw/main/Kubeflow/src/ipynb/kubectl.ipynb
   ```
   - 좌측탭에 kubectl.ipynb 파일 생성 확인

5. speed.ipynb 파일 다운로드
   #### **Lab5-2-5**
   ```bash
   wget https://github.com/kakaocloud-edu/tutorial/raw/main/Kubeflow/src/ipynb/speed.ipynb
   ```

6. Notebooks 탭 > `gpu-notebook`의 `CONNECT` 클릭
   **Note**: `cpu-notebook`, `gpu-notebook` 서로 다름 유의
7. Other 중 `Terminal` 클릭
8. TensorFlow 라이브러리 gpu-notebook에 설치
   #### **Lab5-2-8**
   ```bash
   pip install tensorflow
   ```

9. kubectl.ipynb 파일 다운로드
   #### **Lab5-2-9**
   ```bash
   wget https://github.com/kakaocloud-edu/tutorial/raw/main/Kubeflow/src/ipynb/kubectl.ipynb
   ```
   - 좌측탭에 kubectl.ipynb 파일 생성 확인

10. speed.ipynb 파일 다운로드
    #### **Lab5-2-10**
   ```bash
    wget https://github.com/kakaocloud-edu/tutorial/raw/main/Kubeflow/src/ipynb/speed.ipynb
   ```

## 3. 노트북 속도 비교
1. Notebooks 탭 > `cpu-notebook`의 `CONNECT` 클릭
2. Notebooks 탭 > `gpu-notebook`의 `CONNECT` 클릭
3. cpu-notebook – speed.ipynb `RUN` 클릭

   ![cpu speed run](https://github.com/KOlizer/tutorial/assets/127844467/f8882625-4f13-42d1-a775-1f10524da24a)
   
   - 진행 상황 확인
   
   ![cpu progress](https://github.com/KOlizer/tutorial/assets/127844467/c8a371d6-9b91-4fcb-a293-ee44682a0968)

4. gpu-notebook – speed.ipynb `RUN` 클릭
   **Note**: 위의 cpu-notebook 실습과 동일

   ![gpu speed run](https://github.com/KOlizer/tutorial/assets/127844467/f8882625-4f13-42d1-a775-1f10524da24a)

   - 진행 상황 확인

   ![gpu progress](https://github.com/KOlizer/tutorial/assets/127844467/c8a371d6-9b91-4fcb-a293-ee44682a0968)

5. 결과 값 비교
   - Training time이 서로 다른 것을 확인

     ![cpu training time](https://github.com/KOlizer/tutorial/assets/127844467/0c66ab5b-5aae-4a70-9cce-357e1965bbb5)
     ![gpu training time](https://github.com/KOlizer/tutorial/assets/127844467/6b47a691-640e-4fd6-b857-7c8f05d92a9a)

## 4. Kubeflow Tensorboard
1. Notebooks 탭 > `gpu-notebook`의 `CONNECT` 클릭
2. 위 실행에 의하여 log(logs/fit/) 날짜별로 생성됨을 확인
3. Tensorboards 탭 > `+ New TensorBoard` 클릭
   - Tensorboard 설정 정보
     - 이름 : `tensorboard`
     - `PVC` 클릭
     - PVC name : `cpu-notebook-volume`
     - Mount Path : `logs/fit/`
4. `CREATE` 클릭
5. 생성된 TensorBoard의 `CONNECT` 클릭
6. 생성된 Tensorboards 목록 확인
   1. Scalars (스칼라)
      - 훈련 및 검증 정확도 (Training and Validation Accuracy)
      - 훈련 및 검증 손실 (Training and Validation Loss)
      
        ![tensorboard scalars](https://github.com/KOlizer/tutorial/assets/127844467/451e818d-8593-4ca5-aaf4-82eb0ba9d0a4)

   2. Graphs (그래프)
      - 모델 그래프 시각화 (Model Graph Visualization)
      
        ![tensorboard graphs](https://github.com/KOlizer/tutorial/assets/127844467/1a6dc343-3067-4f7b-adaf-317fcae81418)

   3. Distributions (분포)
      - 가중치 및 편향 분포 (Weights and Biases Distribution)
      
        ![tensorboard distributions](https://github.com/KOlizer/tutorial/assets/127844467/cf7d6531-5768-4e4b-88b2-e9e366558934)

   4. Histogram (히스토그램)
      - 가중치 및 편향 히스토그램 (Weights and Biases Histograms)
      
        ![tensorboard histograms](https://github.com/KOlizer/tutorial/assets/127844467/fc059c5d-45f4-4c47-89f2-e34fff839acb)
