# [Lab] 볼륨, 파일시스템 확장하기

볼륨 크기를 확장 후, 파티션과 파일시스템까지 확장해봅니다.

1. 파티션 정보 확인(lsblk - list block devices)
    ```bash
    lsblk
    ```
2. 파일시스템 정보 확인 (df(disk free) - report file system disk space usage)
    ```bash
    df -Th
    ```
3. growpart 명령어를 통해 파티션을 디스크의 사용 가능한 공간까지 늘림
    ```bash
    growpart /dev/vda 1
    ```
4. 파티션 정보 확인(lsblk - list block devices)
    ```bash
    lsblk
    ```
5. 실제 파일 시스템의 크기는 그에 따라 즉시 변경되지 않음을 확인
    ```bash
    df -Th
    ```
6. 파티션 크기를 늘렸더라도, 파일 시스템 크기는 따로 조정 필요
   - resize2fs 명령어를 통해 파일 시스템 크기 조정(resize2fs - ext2/ext3/ext4 file system resizer)
    ```bash
    sudo resize2fs /dev/vda1
    ```
7. 다시 크기 확인
    ```bash
    df -Th
    ```
