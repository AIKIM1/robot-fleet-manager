# Release Notes

## v0.1.0 - Robot Fleet Manager

### 개발 내용

- FastAPI 기반 로봇 Fleet 관리 백엔드 구현
- WebSocket 실시간 시뮬레이션 상태 전송 구현
- React + TypeScript + Three.js 기반 3D 관제 대시보드 구현
- 택배 입고, 로봇 배정, 이동, 분류, 복귀, 충전 흐름 구현
- 배터리, 처리량, 정확도, 가동률 KPI 표시
- REST API로 로봇 조회, 명령 전송, 전체 명령, 시뮬레이션 제어 지원
- pytest 테스트 구조와 GitLab CI 파이프라인 포함
- MuJoCo 연동 가능한 구조와 mock 시뮬레이션 fallback 제공

### 확인 내용

- 백엔드 주요 Python 파일 문법 체크 완료
- `scripts/run_sim.py --robots 2 --steps 20` 실행 확인

### 다음 개발 예정

- A* 경로 탐색 추가
- 시나리오 기반 회귀 테스트 추가
- GitLab CI 시뮬레이션 검증 강화
- MES/WMS 연동 포트폴리오 방향으로 확장
