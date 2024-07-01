# [Demo] Bare Metal Server 실습

볼륨 크기를 확장 후, 파티션과 파일시스템까지 확장해봅니다.

1. bastion VM 가상머신 CMD 창에서
    1. Hypervisor 체크
        ```bash
        lscpu
        ```
    - 결과: Hypervisor vendor: KVM
    2. 가상화 확인
        ```bash
        systemd-detect-virt
        ```
    - 결과: kvm
2. 베어메탈 CMD 창에서
    1. Hypervisor 체크
        ```bash
        lscpu
        ```
    - 결과: "Hypervisor vendor:" 가 없음
    2. 가상화 확인
        ```bash
        systemd-detect-virt
        ```
    - 결과: none
3. master와 slave 인터페이스 확인
    ```bash
    ip address
    ```
4. LACP(Link Aggregation Control Protocol) 모드 4 확인 및 대역폭 확인
    ```bash
    cat /proc/net/bonding/bond0
    ```
