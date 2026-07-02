# SafeVision-AI

YOLO 기반 PPE 작업자 안전 모니터링 프로젝트입니다.

## Project Overview

작업자의 안전모 및 안전조끼 착용 여부를 실시간으로 감지하고, 위험구역 침입 여부를 판단하여 안전 이벤트를 기록하는 시스템입니다.

## Main Features

- 실시간 작업자 감지
- 안전모 착용 / 미착용 감지
- 안전조끼 착용 / 미착용 감지
- 위험구역 침입 판단
- 위반 이벤트 로그 기록
- CCTV 관리 화면 제공

## Class Names

| Class ID | Class Name |
| -------: | ---------- |
| 0 | no_helmet |
| 1 | helmet |
| 2 | no_safety_vest |
| 3 | safety_vest |
| 4 | person |

## Folder Structure

```text
SafeVision-AI/
├─ ai/
│  ├─ datasets/
│  ├─ models/
│  │  └─ weights/
│  ├─ detect.py
│  └─ train.py
├─ backend/
│  ├─ app.py
│  └─ requirements.txt
├─ frontend/
├─ docs/
│  ├─ class_names.md
│  └─ roles.md
└─ README.md
```

## Tech Stack

- Python
- YOLO
- OpenCV
- FastAPI
- HTML/CSS/JavaScript