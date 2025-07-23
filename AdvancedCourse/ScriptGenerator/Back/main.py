from fastapi import FastAPI, HTTPException, Body  # FastAPI 관련 모듈 가져오기
from pydantic import BaseModel  # 데이터 검증을 위한 Pydantic 모듈 가져오기
import requests  # HTTP 요청을 보내기 위한 requests 모듈 가져오기
from fastapi.middleware.cors import CORSMiddleware  # CORS 설정을 위한 모듈 가져오기
import yaml  # YAML 데이터를 처리하기 위한 모듈 가져오기
import json  # JSON 데이터를 처리하기 위한 모듈 가져오기

# FastAPI 애플리케이션 생성
app = FastAPI()

# CORS 미들웨어 추가
# CORS(Cross-Origin Resource Sharing)는 다른 출처의 웹 페이지가 API에 접근할 수 있도록 허용하는 것
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 출처 허용
    allow_credentials=True,  # 자격 증명 허용
    allow_methods=["*"],  # 모든 HTTP 메서드 허용
    allow_headers=["*"],  # 모든 헤더 허용
)

# 사용자 자격 증명을 정의하는 Pydantic 모델
class UserCredentials(BaseModel):
    access_key_id: str  # 액세스 키 ID
    access_key_secret: str  # 액세스 키 비밀

# 클러스터 자격 증명을 정의하는 Pydantic 모델
class ClusterCredentials(UserCredentials):
    cluster_name: str  # 클러스터 이름

# 인스턴스 세트 자격 증명을 정의하는 Pydantic 모델
class InstanceSetCredentials(UserCredentials):
    instance_set_name: str  # 인스턴스 세트 이름

# Kafka 클러스터 자격 증명을 정의하는 Pydantic 모델
class KafkaClusterCredentials(UserCredentials):
    kafka_cluster_name: str  # Kafka 클러스터 이름

# Kafka 클러스터 ID 자격 증명을 정의하는 Pydantic 모델
class KafkaClusterIdCredentials(UserCredentials):
    cluster_id: str  # Kafka 클러스터 ID



# Kakao Cloud IAM에서 토큰과 사용자/프로젝트 정보를 가져오는 함수
def get_token_and_details(credentials: UserCredentials):
    url = "https://iam.kakaocloud.com/identity/v3/auth/tokens"  # 토큰을 요청할 URL
    payload = {
        "auth": {
            "identity": {
                "methods": ["application_credential"],  # 애플리케이션 자격 증명을 사용한 인증
                "application_credential": {
                    "id": credentials.access_key_id,  # 사용자로부터 받은 ID
                    "secret": credentials.access_key_secret,  # 사용자로부터 받은 비밀
                },
            }
        }
    }
    headers = {"Content-Type": "application/json"}  # 요청 헤더에 콘텐츠 타입 지정
    response = requests.post(url, json=payload, headers=headers)  # POST 요청을 보내서 토큰을 받음
    if response.status_code != 201:  # 응답 상태 코드가 201이 아니면 에러 발생
        raise HTTPException(status_code=response.status_code, detail=response.text)

    token = response.headers.get("X-Subject-Token")  # 응답 헤더에서 토큰 가져오기
    response_json = response.json()  # 응답을 JSON으로 변환
    user_id = response_json.get("token", {}).get("user", {}).get("id", {})  # 사용자 ID 가져오기
    domain_id = (
        response_json.get("token", {}).get("user", {}).get("domain", {}).get("id")
    )  # 도메인 ID 가져오기
    domain_name = (
        response_json.get("token", {}).get("user", {}).get("domain", {}).get("name")
    )  # 도메인 이름 가져오기
    project_id = response_json.get("token", {}).get("project", {}).get("id")  # 프로젝트 ID 가져오기
    project_name = response_json.get("token", {}).get("project", {}).get("name")  # 프로젝트 이름 가져오기

    return {
        "token": token,
        "user_id": user_id,
        "domain_id": domain_id,
        "domain_name": domain_name,
        "project_id": project_id,
        "project_name": project_name,
    }

# 토큰 세부 정보를 가져오는 엔드포인트
@app.post("/get-token-details")
def get_token_details(credentials: UserCredentials):
    return get_token_and_details(credentials)

# 클러스터 목록을 가져오는 엔드포인트
@app.post("/get-clusters")
def get_clusters(credentials: UserCredentials):
    details = get_token_and_details(credentials)
    url = "https://d801c895-f7a2-4cae-9d6e-a4f7e68f1039.api.kr-central-2.kakaoi.io/api/v1/clusters"
    headers = {
        "Origin": "https://console.kakaocloud.com",
        "Referer": "https://console.kakaocloud.com",
        "X-Auth-token": details["token"],
        "X-Kep-Project-Domain-Id": details["domain_id"],
        "X-Kep-Project-Domain-Name": details["domain_name"],
        "X-Kep-Project-Id": details["project_id"],
        "X-Kep-Project-Name": details["project_name"],
    }
    response = requests.get(url, headers=headers)
    if response.status_code != 200:  # 응답 상태 코드가 200이 아니면 에러 발생
        raise HTTPException(status_code=response.status_code, detail=response.text)
    return response.json()

# 프로젝트 이름을 가져오는 엔드포인트
@app.post("/get-project-name")
def get_project_name(credentials: UserCredentials):
    details = get_token_and_details(credentials)
    return {"project_name": details["project_name"]}

# 클러스터의 kubeconfig를 가져오는 엔드포인트
@app.post("/get-kubeconfig")
def get_kubeconfig(credentials: ClusterCredentials):
    details = get_token_and_details(credentials)
    url = f"https://d801c895-f7a2-4cae-9d6e-a4f7e68f1039.api.kr-central-2.kakaoi.io/api/v1/clusters/{credentials.cluster_name}/kubeconfig"
    headers = {
        "Origin": "https://console.kakaocloud.com",
        "Referer": "https://console.kakaocloud.com",
        "X-Auth-token": details["token"],
        "X-Kep-Project-Domain-Id": details["domain_id"],
        "X-Kep-Project-Domain-Name": details["domain_name"],
        "X-Kep-Project-Id": details["project_id"],
        "X-Kep-Project-Name": details["project_name"],
    }
    response = requests.get(url, headers=headers)

    if response.status_code != 200:  # 응답 상태 코드가 200이 아니면 에러 발생
        raise HTTPException(status_code=response.status_code, detail=response.text)

    try:
        kubeconfig_yaml = response.text
        kubeconfig_json = yaml.safe_load(kubeconfig_yaml)  # YAML 응답을 JSON으로 변환
        return kubeconfig_json
    except yaml.YAMLError as e:
        raise HTTPException(status_code=500, detail="YAML 응답을 파싱하는 중 오류 발생")

# 인스턴스 그룹 목록을 가져오는 엔드포인트
@app.post("/get-instance-groups")
def get_instance_groups(credentials: UserCredentials):
    details = get_token_and_details(credentials)
    url = "https://231b3efe-0491-46d5-ba7f-5ec1679796e2.api.kr-central-2.kakaoi.io/instance-sets"
    headers = {
        "Origin": "https://console.kakaocloud.com",
        "Referer": "https://console.kakaocloud.com",
        "X-Auth-token": details["token"],
        "X-Kep-Project-Domain-Id": details["domain_id"],
        "X-Kep-Project-Domain-Name": details["domain_name"],
        "X-Kep-Project-Id": details["project_id"],
        "X-Kep-Project-Name": details["project_name"],
    }
    response = requests.get(url, headers=headers)

    if response.status_code != 200:  # 응답 상태 코드가 200이 아니면 에러 발생
        raise HTTPException(status_code=response.status_code, detail=response.text)

    instance_groups = response.json()
    instance_set_names = [item["instanceSet"]["instanceSetName"] for item in instance_groups["instanceSetWithStatusList"]]
    return instance_set_names

# 인스턴스 엔드포인트를 가져오는 엔드포인트
@app.post("/get-instance-endpoints")
def get_instance_endpoints(credentials: InstanceSetCredentials):
    details = get_token_and_details(credentials)
    url = "https://231b3efe-0491-46d5-ba7f-5ec1679796e2.api.kr-central-2.kakaoi.io/instance-sets"
    headers = {
        "X-Auth-token": details["token"],
        "X-Kep-Project-Domain-Id": details["domain_id"],
        "X-Kep-Project-Domain-Name": details["domain_name"],
        "X-Kep-Project-Id": details["project_id"],
        "X-Kep-Project-Name": details["project_name"],
    }
    response = requests.get(url, headers=headers)
    if response.status_code != 200:  # 응답 상태 코드가 200이 아니면 에러 발생
        raise HTTPException(status_code=response.status_code, detail=response.text)

    data = response.json()
    instance_set = next((item for item in data.get("instanceSetWithStatusList", []) if item["instanceSet"]["instanceSetName"] == credentials.instance_set_name), None)
    if instance_set is None:
        raise HTTPException(status_code=404, detail="인스턴스 세트를 찾을 수 없음")
    
    endpoints = instance_set.get("instanceSet", {}).get("endpoint", [])
    primary = endpoints[0] if endpoints else None
    standby = endpoints[1] if len(endpoints) > 1 else "없음"

    return {"primary_endpoint": primary, "standby_endpoint": standby}

# 사용자와 연관된 프로젝트 목록을 가져오는 엔드포인트
@app.post("/get-projects")
def get_projects(credentials: UserCredentials):
    details = get_token_and_details(credentials)
    url = f"https://iam.kakaocloud.com/identity/v3/users/{details['user_id']}/projects"
    headers = {"X-Auth-token": details["token"]}
    response = requests.get(url, headers=headers)
    if response.status_code != 200:  # 응답 상태 코드가 200이 아니면 에러 발생
        raise HTTPException(status_code=response.status_code, detail=response.text)

    return response.json()

# Kafka 클러스터 목록을 가져오는 엔드포인트 (올바른 파싱)
@app.post("/get-kafka-clusters")
def get_kafka_clusters(credentials: UserCredentials):
    """
    실제 API 응답 구조에 맞춘 Kafka 클러스터 목록 조회
    """
    details = get_token_and_details(credentials)
    
    url = f"https://advanced-managed-kafka.kr-central-2.kakaocloud.com/v1/api/{details['project_id']}/kafka-clusters"
    
    headers = {
        "Origin": "https://console.kakaocloud.com",
        "Referer": "https://console.kakaocloud.com",
        "X-Auth-token": details["token"],
        "X-Kep-Project-Domain-Id": details["domain_id"],
        "X-Kep-Project-Domain-Name": details["domain_name"],
        "X-Kep-Project-Id": details["project_id"],
        "X-Kep-Project-Name": details["project_name"],
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code, 
                detail=f"Kafka API 호출 실패: {response.text}"
            )
        
        clusters_data = response.json()
        
        # 올바른 파싱: kafka_clusters 키에서 배열 추출
        kafka_clusters = clusters_data.get("kafka_clusters", [])
        
        # 클러스터 기본 정보 추출
        cluster_info = []
        for cluster in kafka_clusters:
            cluster_info.append({
                "id": cluster.get("id"),
                "name": cluster.get("name"),
                "status": cluster.get("status"),
                "version": cluster.get("version"),
                "bootstrap_servers": cluster.get("bootstrap_servers"),
                "total_broker_count": cluster.get("total_broker_count"),
                "instance_type": cluster.get("instance_type")
            })
        
        # 클러스터 이름만 추출
        cluster_names = [cluster.get("name") for cluster in kafka_clusters]
        
        return {
            "kafka_cluster_names": cluster_names,
            "cluster_details": cluster_info,
            "total_clusters": len(kafka_clusters),
            "project_id": details["project_id"],
            "project_name": details["project_name"]
        }
        
    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=503,
            detail=f"Kafka API 연결 오류: {str(e)}"
        )



# Kafka 부트스트랩 서버 정보를 가져오는 엔드포인트 (최적화 버전)
@app.post("/get-kafka-bootstrap-servers")
def get_kafka_bootstrap_servers(credentials: KafkaClusterCredentials):
    """
    전체 클러스터 목록에서 특정 클러스터의 부트스트랩 서버 정보 추출
    """
    details = get_token_and_details(credentials)
    
    url = f"https://advanced-managed-kafka.kr-central-2.kakaocloud.com/v1/api/{details['project_id']}/kafka-clusters"
    
    headers = {
        "Origin": "https://console.kakaocloud.com",
        "Referer": "https://console.kakaocloud.com",
        "X-Auth-token": details["token"],
        "X-Kep-Project-Domain-Id": details["domain_id"],
        "X-Kep-Project-Domain-Name": details["domain_name"],
        "X-Kep-Project-Id": details["project_id"],
        "X-Kep-Project-Name": details["project_name"],
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Kafka API 호출 실패: {response.text}"
            )
        
        clusters_data = response.json()
        kafka_clusters = clusters_data.get("kafka_clusters", [])
        
        # 특정 클러스터 찾기
        target_cluster = None
        for cluster in kafka_clusters:
            if cluster.get("name") == credentials.kafka_cluster_name:
                target_cluster = cluster
                break
        
        if not target_cluster:
            raise HTTPException(
                status_code=404,
                detail=f"클러스터 '{credentials.kafka_cluster_name}'을 찾을 수 없음. 사용 가능한 클러스터: {[c.get('name') for c in kafka_clusters]}"
            )
        
        # 부트스트랩 서버 정보 추출 (이미 문자열로 제공됨)
        bootstrap_servers_str = target_cluster.get("bootstrap_servers", "")
        bootstrap_servers_list = [server.strip() for server in bootstrap_servers_str.split(",") if server.strip()]
        
        # 브로커 세부 정보
        brokers_info = []
        for broker in target_cluster.get("kafka_brokers", []):
            brokers_info.append({
                "broker_id": broker.get("broker_id"),
                "ip": broker.get("ip"),
                "status": broker.get("status"),
                "availability_zone": broker.get("availability_zone"),
                "volume_size": broker.get("volume_size")
            })
        
        return {
            "cluster_id": target_cluster.get("id"),
            "kafka_cluster_name": credentials.kafka_cluster_name,
            "bootstrap_servers": bootstrap_servers_list,
            "connection_string": bootstrap_servers_str,
            "cluster_status": target_cluster.get("status"),
            "kafka_version": target_cluster.get("version"),
            "total_broker_count": target_cluster.get("total_broker_count"),
            "broker_port": target_cluster.get("broker_port"),
            "instance_type": target_cluster.get("instance_type"),
            "brokers_detail": brokers_info
        }
        
    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=503,
            detail=f"Kafka API 연결 오류: {str(e)}"
        )
    
# 클러스터 ID로 Kafka 부트스트랩 서버 정보를 가져오는 엔드포인트
@app.post("/get-kafka-bootstrap-servers-by-id")
def get_kafka_bootstrap_servers_by_id(credentials: KafkaClusterIdCredentials):
    """
    클러스터 ID를 사용하여 특정 클러스터의 부트스트랩 서버 정보 조회
    """
    details = get_token_and_details(credentials)
    
    url = f"https://advanced-managed-kafka.kr-central-2.kakaocloud.com/v1/api/{details['project_id']}/kafka-clusters"
    
    headers = {
        "Origin": "https://console.kakaocloud.com",
        "Referer": "https://console.kakaocloud.com",
        "X-Auth-token": details["token"],
        "X-Kep-Project-Domain-Id": details["domain_id"],
        "X-Kep-Project-Domain-Name": details["domain_name"],
        "X-Kep-Project-Id": details["project_id"],
        "X-Kep-Project-Name": details["project_name"],
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Kafka API 호출 실패: {response.text}"
            )
        
        clusters_data = response.json()
        kafka_clusters = clusters_data.get("kafka_clusters", [])
        
        # 클러스터 ID로 특정 클러스터 찾기
        target_cluster = None
        for cluster in kafka_clusters:
            if cluster.get("id") == credentials.cluster_id:
                target_cluster = cluster
                break
        
        if not target_cluster:
            raise HTTPException(
                status_code=404,
                detail=f"클러스터 ID '{credentials.cluster_id}'를 찾을 수 없음"
            )
        
        # 부트스트랩 서버 정보 추출
        bootstrap_servers_str = target_cluster.get("bootstrap_servers", "")
        bootstrap_servers_list = [server.strip() for server in bootstrap_servers_str.split(",") if server.strip()]
        
        return {
            "cluster_id": target_cluster.get("id"),
            "kafka_cluster_name": target_cluster.get("name"),
            "bootstrap_servers": bootstrap_servers_list,
            "connection_string": bootstrap_servers_str,
            "cluster_status": target_cluster.get("status"),
            "kafka_version": target_cluster.get("version")
        }
        
    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=503,
            detail=f"Kafka API 연결 오류: {str(e)}"
        )




# 스크립트가 직접 실행될 경우 uvicorn을 사용하여 앱 실행
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
