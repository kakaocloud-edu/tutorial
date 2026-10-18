# Kubernetes 실습 웹사이트 — 스크롤 소개 화면 추가 버전

이 디렉터리는 기존 `AdvancedCourse/src/spring`과 나란히 보관하는 개선 버전입니다. **현재 강의의 기본 배포 경로에는 연결하지 않았습니다.** 기존 초기화 스크립트는 계속 `src/spring`을 복사하므로, `spring-code`를 저장소에 올리는 것만으로 기존 수강생의 실습 화면이나 배포 동작이 바뀌지 않습니다.

나중에 강의에 적용할 때 사용할 완전한 Spring Boot 소스와 이미지 자산을 포함합니다. Java 17 이상을 사용하며, 기본 포트는 8080입니다.

## 추가된 화면

- `/`의 첫 화면에는 기존 환영 문구, 배경 그라데이션, 왼쪽 위 파란색·노란색 원, Pod 호스트 이름, DB 버튼을 유지했습니다.
- 스크롤하면 두 원이 이동하면서 클라우드 그래픽으로 이어지고, 관리형 Kubernetes → 여러 가용 영역 → VPC·클라우드 서비스 연결 문구가 나타났다 사라집니다. 위로 올리면 원래 화면으로 복원됩니다.
- 승인한 수정 영상의 23.625초·1280×720·24fps를 WebP 567장으로 포함했습니다. 불필요한 선과 오른쪽 아래 Veo 표시를 정리한 사이트용 마스터를 사용합니다. 장면은 잘라내지 않고 화면 안에 전체가 들어오도록 표시합니다.
- 첫 화면에서는 영상 이미지를 요청하지 않습니다. 스크롤 이후 필요한 프레임부터 요청하며, 동시 요청은 4개, 스크립트의 이미지 캐시는 14개로 제한했습니다.
- 모바일·작은 높이의 화면·움직임 줄이기 설정에서는 정지 이미지와 소개 문구를 표시합니다. `/experience`에는 별도의 독립 소개 시안을 유지했습니다.
- ‘실습으로 돌아가기’는 페이지를 다시 요청하지 않고 위로 이동하므로, 열어 둔 DB 패널과 조회 결과가 유지됩니다.

영상 자산은 `src/main/resources/static/experience/film/`에 있습니다. 원본 정보·프레임 수·바이트 수는 그 안의 `manifest.json`에 기록했습니다. 실행할 때 Google Flow 로그인이나 외부 영상 서비스 연결이 필요하지 않습니다. 재생성 방법과 세부 동작은 [EXPERIENCE.md](EXPERIENCE.md)를 참고하세요.

## 기존 코드와의 차이

| 파일 그룹 | 변경 내용 |
|---|---|
| `templates/welcome.html` | 실습 화면을 감싸는 레이아웃과 소개 fragment 연결을 추가하고 CSS 적용 범위를 구분했습니다. 기존 실습 `.content`와 인라인 DB JavaScript는 그대로입니다. |
| `fragments/immersive-story.html`, `static/experience/immersive.css`, `immersive.js` | 원의 이동, 영상 프레임 표시, 소개 문구의 등장·퇴장, 실습 복귀를 담당하는 새 파일입니다. |
| `static/experience/film/` | 실제 영상의 WebP 567장과 정지 포스터, 변환 정보를 담은 manifest를 추가했습니다. |
| `ExperienceController.java`, `experience.html`, 독립 화면 fragment·CSS·JavaScript·SVG 자산 | `/experience`에서 확인하는 별도 소개 시안입니다. 기존 DB 컨트롤러와 분리했습니다. |
| 테스트·문서·`tools/` | 실습 계약과 자산 응답을 확인하는 테스트, 사용·전환 안내, 프레임 생성 도구를 추가했습니다. |

원래의 Java 파일 4개인 `DemoApplication.java`, `HelloController.java`, `DatabaseConfig.java`, `DatabaseApiController.java`와 `pom.xml`, `application.properties`, Maven Wrapper(`mvnw`, `mvnw.cmd`, `.mvn/`)는 변경하지 않았습니다.

## 유지한 실습 동작

`WELCOME_MESSAGE`, `BACKGROUND_COLOR`, 호스트 이름 표시와 `/`, `/db1`, `/db2`의 기존 동작을 유지했습니다. `HelloController.java`, `DatabaseApiController.java`, `DatabaseConfig.java`, `pom.xml`과 기존 실습 콘텐츠·DB 요청 스크립트는 원본을 유지합니다.

- `BACKGROUND_COLOR`는 기존처럼 `#1a1a2e`에서 지정 색상으로 이어지는 그라데이션의 끝 색입니다. 강의 매니페스트의 기본 예시는 `#4a69bd`, Lab07의 변경 예시는 `#4287f5`입니다. 환경 변수가 없으면 `#1a1a2e`를 사용합니다.
- ConfigMap 변경은 기존 강의처럼 적용 후 Deployment를 재시작해야 실행 중인 Pod의 환경 변수에 반영됩니다.
- `/db1`은 첫 번째 DB에 데이터를 삽입한 뒤 조회합니다. `/db2`는 두 번째 DB를 조회합니다. 스크롤 소개 기능은 이 두 API를 자동 호출하지 않습니다.
- 화면의 그래픽은 서비스 소개를 위한 추상 표현입니다. 실제 클러스터 상태나 HPA 동작을 표시하는 기능은 아닙니다.

## 나중에 강의에서 활성화하기

아직 `AdvancedCourse/src/script/script.sh`는 변경하지 않았습니다. 적용 시점에 아래 복사 명령 한 줄을 바꿉니다. 뒤에 붙은 기존 오류 처리 구문은 유지합니다.

기존:

```sh
sudo cp -r /home/ubuntu/tutorial/AdvancedCourse/src/spring /home/ubuntu/
```

변경:

```sh
sudo cp -r /home/ubuntu/tutorial/AdvancedCourse/src/spring-code /home/ubuntu/spring
```

**복사 대상은 `/home/ubuntu/spring`으로 유지해야 합니다.** 이후 Lab04의 `cd /home/ubuntu/spring`, Maven 명령, Dockerfile의 JAR 경로를 그대로 사용하기 위해서입니다.

이 한 줄은 `/home/ubuntu/spring`이 없는 새 VM에 적용하는 경우를 기준으로 합니다. 대상 디렉터리가 이미 있으면 `cp -r`은 그 안에 `spring-code` 디렉터리를 만들 수 있으므로, 기존 VM에서는 아래 백업·교체 절차를 사용하세요. 기존 디렉터리에 단순히 덮어 복사하면 이전 빌드 파일이 섞일 수도 있습니다.

### 기존 VM에서 소스를 바꿀 때

다음 예시는 기존 소스를 삭제하지 않고 시간 이름의 백업으로 옮긴 후, 비어 있는 대상 경로에 새 소스를 복사합니다. 먼저 이 버전이 저장소에 반영되어 있어야 합니다. 저장소 업데이트가 로컬 변경이나 다른 이유로 실패하면 중단하고 그 원인을 확인하세요.

```sh
set -e

cd /home/ubuntu/tutorial
git pull --ff-only
test -f /home/ubuntu/tutorial/AdvancedCourse/src/spring-code/pom.xml

spring_backup=""
if [ -e /home/ubuntu/spring ]; then
    spring_backup="/home/ubuntu/spring-backup-$(date +%Y%m%d-%H%M%S)"
    test ! -e "$spring_backup"
    sudo mv -- /home/ubuntu/spring "$spring_backup"
    printf '기존 소스 백업: %s\n' "$spring_backup"
fi

sudo cp -r -- /home/ubuntu/tutorial/AdvancedCourse/src/spring-code /home/ubuntu/spring
sudo chown -R ubuntu:ubuntu /home/ubuntu/spring
sudo chmod +x /home/ubuntu/spring/mvnw
```

직접 작성한 Dockerfile이나 추가 설정은 백업을 확인하고 필요한 항목만 새 소스로 옮기세요. 이전 `target/`은 복사하지 않고 다시 빌드합니다. 이 절차는 소스 폴더를 바꾸는 작업이며, 이미 실행 중인 컨테이너나 Kubernetes Deployment를 자동으로 바꾸지는 않습니다.

## 빌드와 실행

활성화 후에도 기존 Maven·Docker 절차와 JAR 이름을 그대로 사용합니다.

```sh
cd /home/ubuntu/spring
./mvnw clean package
java -jar target/demo-0.0.1-SNAPSHOT.jar
```

직접 실행한 로컬 확인 주소는 `http://localhost:8080/`입니다. 컨테이너 배포는 Lab04의 Dockerfile 생성·이미지 빌드·레지스트리 업로드 절차를 따릅니다. Dockerfile의 `COPY target/demo-0.0.1-SNAPSHOT.jar demo.jar`도 같습니다. Kubernetes에 적용할 때는 새 이미지를 배포해야 화면이 바뀝니다.

이 저장소 안에서 별도로 확인하려면 `AdvancedCourse/src/spring-code`에서 `./mvnw spring-boot:run`을 실행할 수 있습니다. Windows에서는 `mvnw.cmd`를 사용하세요.

## 확인 범위

- 새 `AdvancedCourse/src/spring-code` 경로에서 Java 17로 `./mvnw clean verify`를 실행해 테스트 6개, 실패·오류 0개로 빌드에 성공했습니다. 실제 Spring·Thymeleaf 렌더링, 이미지 지연 로딩, WebP 자산 응답과 조건부 요청, 모의 DB를 이용한 기존 API 계약을 확인했습니다.
- 로컬 브라우저에서 첫 화면 보존, 정방향·역방향 스크롤, 장면과 문구 연결, 열린 DB 패널 유지, 모바일 정적 전환을 확인했습니다.
- 이미지 교체 후 이전 브라우저 캐시가 남지 않도록 프레임·포스터 URL에 `?v=2`를 사용합니다. 같은 파일 이름으로 자산을 다시 교체하면 관련 URL의 버전도 함께 올려야 합니다.
- 실제 운영 DB 및 Kubernetes 환경의 가용 영역·Pod 분산·HPA는 이 로컬 검증 환경에 구성하지 않았습니다. 강의 활성화 전에 해당 환경에서 기존 실습 절차를 확인하세요. 자동 테스트는 모의 DB를 사용하며 실제 DB에 데이터를 삽입하지 않습니다.
