# 택배 분류 로봇 시뮬레이션

실제 물류센터의 택배 분류 로봇 시스템을 시뮬레이션하는 웹 기반 3D 대시보드입니다.

![Python](https://img.shields.io/badge/Python-3.12+-blue)
![React](https://img.shields.io/badge/React-18-61DAFB)
![Three.js](https://img.shields.io/badge/Three.js-3D-black)
![FastAPI](https://img.shields.io/badge/FastAPI-WebSocket-009688)

## 주요 기능

- **3D 실시간 시뮬레이션** - 6대의 AGV 로봇이 창고에서 택배를 분류하는 과정을 3D로 시각화
- **컨베이어 벨트** - 택배가 입고되어 벨트 위에 놓이고, 로봇이 가져가는 과정을 시각적으로 표현
- **8개 분류 구역** - 서울, 경기, 인천, 부산, 대구, 광주, 대전, 기타
- **배터리 관리** - 실시간 충방전 시뮬레이션, 자동 충전소 이동 (Geek+ S-Series 기준)
- **충돌 회피** - 로봇 간 반경 기반 자동 감속/회피
- **실시간 KPI** - 처리량/시, 정확도(99.9%), 평균 배터리, 가동률
- **이벤트 로그** - 택배 입고/배정/배달/충전/오분류 실시간 기록
- **명령 제어** - 개별/전체 로봇 정지, 충전, 초기화, 통계 리셋

## 기술 스택

| 구분 | 기술 |
|---|---|
| 백엔드 | Python 3.12+, FastAPI, WebSocket, MuJoCo (선택) |
| 프론트엔드 | React 18, TypeScript, Three.js (react-three-fiber) |
| 통신 | WebSocket (30Hz 실시간 스트리밍), REST API |
| 시뮬레이션 | MuJoCo 물리엔진 또는 내장 Mock 시뮬레이션 |

## 실행 방법

### 1. 저장소 클론

```bash
git clone https://github.com/AIKIM1/robot-fleet-manager.git
cd robot-fleet-manager
```

### 2. 백엔드 설치 및 실행

```bash
pip install -e ".[test]"
python -m uvicorn src.main:app --host 0.0.0.0 --port 8000
```

### 3. 프론트엔드 설치 및 실행

```bash
cd frontend
npm install
npm run dev -- --port 3001
```

### 4. 브라우저에서 확인

```text
http://localhost:3001
```

> MuJoCo가 설치되어 있지 않아도 내장 Mock 시뮬레이션으로 자동 동작합니다.

## 테스트

```bash
python -m pytest tests/ -v
```

## API 문서

```text
http://localhost:8000/docs
```

## 라이선스

MIT
