# SafeVision-AI

YOLO 기반 PPE 작업자 안전 모니터링 프로젝트입니다.

## Project Overview

작업자의 안전모 및 안전조끼 착용 여부를 실시간으로 감지하고, 위험구역 진입 여부를 판단하여 안전 이벤트를 기록하는 시스템입니다.

관리자는 웹 화면을 통해 전체 안전 상태, 실시간 CCTV 감지 현황, 이벤트 로그, 통계 분석 정보를 확인할 수 있습니다.

## Main Features

- 실시간 작업자 감지
- 안전모 착용 / 미착용 감지
- 안전조끼 착용 / 미착용 감지
- 위험구역 진입 판단
- 위험도 점수 기반 안전 등급 분류
- 위반 이벤트 로그 기록
- 이벤트 처리 상태 관리
- 기간별 통계 분석 화면 제공

## Page Structure

### 1. 로그인 화면

관리자가 시스템에 접근하기 위한 로그인 화면입니다.

- 관리자 아이디 / 비밀번호 입력
- 아이디 저장 기능
- 로그인 성공 시 대시보드 화면으로 이동
- 로그아웃 후 로그인 화면으로 복귀

### 2. 공통 사이드바

모든 주요 화면에서 공통으로 사용하는 좌측 사이드바입니다.

- SafeVision AI 로고 표시
- 대시보드, 실시간 모니터링, 이벤트 로그, 통계 분석 메뉴 이동
- 현재 페이지 active 표시
- 로그아웃 버튼 제공

### 3. 대시보드 화면

시스템의 전체 안전 상태를 한눈에 확인하는 메인 화면입니다.

- 전체 안전 상태 표시
- 오늘 전체 경고 건수 표시
- PPE 착용률 표시
- CCTV 연결 상태 표시
- 최근 이벤트 목록 표시

### 4. 실시간 모니터링 화면

CCTV별 실시간 감지 상태를 확인하는 화면입니다.

- CCTV 선택 기능
- 실시간 영상 표시 영역
- 현재 위험도 표시
- 위험도 점수 표시
- 안전모 미착용, 안전조끼 미착용, 위험구역 진입 현황 표시

### 5. 이벤트 로그 화면

감지된 위험 이벤트를 목록으로 확인하고 상세 정보를 관리하는 화면입니다.

- 기간별 이벤트 조회
- CCTV별 이벤트 필터링
- 이벤트 번호, 시간, CCTV, 위반 유형, 위험도, 처리 상태 표시
- 이벤트 상세 모달 제공
- 처리 상태 변경
- 메모 입력 기능

### 6. 통계 분석 화면

감지 결과를 통계적으로 확인하는 화면입니다.

- 기간별 통계 조회
- 전체 감지 건수 표시
- 전체 경고 건수 표시
- PPE 착용률 표시
- 위험도 점수 표시
- 시간대별 경고 횟수 차트
- 위반 유형별 비율 차트

## Current Implementation Status

- HTML, CSS, JavaScript 기반 화면 구현
- Flask 기반 화면 라우팅 구성
- Pretendard 글꼴 적용
- SafeVision-AI 전용 초록색 UI 컬러 적용
- 공통 사이드바 구성
- 페이지 이동 구조 정리
- 로그인 / 로그아웃 기본 흐름 구현
- 대시보드, 실시간 모니터링, 이벤트 로그, 통계 분석 화면 1차 구현

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
│  ├─ flask_app.py
│  └─ requirements.txt
├─ static/
│  ├─ css/
│  ├─ js/
│  └─ img/
├─ templates/
│  ├─ login.html
│  ├─ dashboard.html
│  ├─ monitoring.html
│  ├─ event-log.html
│  ├─ statistics.html
│  └─ sidebar.html
├─ docs/
│  ├─ class_names.md
│  └─ roles.md
└─ README.md