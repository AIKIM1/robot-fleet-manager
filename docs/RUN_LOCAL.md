# 로컬 실행 방법

## 1. 프로젝트 위치로 이동

```powershell
cd C:\Users\21ckd\Documents\Codex\2026-05-21\github-pr\robot-fleet-manager-master\robot-fleet-manager-master
```

## 2. 백엔드 실행

```powershell
.\.venv\Scripts\python.exe -m uvicorn src.main:app --host 127.0.0.1 --port 8000
```

## 3. 프론트엔드 실행

새 PowerShell 터미널에서 실행합니다.

```powershell
cd C:\Users\21ckd\Documents\Codex\2026-05-21\github-pr\robot-fleet-manager-master\robot-fleet-manager-master\frontend
$env:PATH='C:\Users\21ckd\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin;' + $env:PATH
& 'C:\Users\21ckd\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe' '..\.tools\npm\bin\npm-cli.js' run dev -- --host 127.0.0.1 --port 3001
```

## 4. 접속 주소

- 프론트엔드: http://127.0.0.1:3001
- API 문서: http://127.0.0.1:8000/docs
- API 상태 확인: http://127.0.0.1:8000/api/simulation/status

## 5. 테스트 실행

```powershell
cd C:\Users\21ckd\Documents\Codex\2026-05-21\github-pr\robot-fleet-manager-master\robot-fleet-manager-master
.\.venv\Scripts\python.exe -m pytest tests/ -q
```

## 참고

- MuJoCo가 없어도 mock 시뮬레이션으로 실행됩니다.
- 프론트엔드 포트는 `3001`, 백엔드 포트는 `8000`입니다.
- 로컬 환경에서 `npm` 명령이 없을 수 있어, 위 명령은 프로젝트에 내려받은 npm CLI를 Node로 직접 실행합니다.
