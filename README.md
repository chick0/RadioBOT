# 새로운 프로젝트로 대체됨

https://github.com/chick0/discord_radio
---
# RadioBOT
- discord.py를 사용해서 만든 디스코드 라디오 봇

## 실행 전 설정
1. ffmpeg 다운받기 (이미 받았다면 상관X)
2. 음악 풀더에 음악 채우기 ( 기본위치: ./data/music/ )
    1. 또는 본인의 음악 풀더로 설정 수정하기
3. 디스코드 개발자 센터에서 자신의 봇 만들기
4. 토큰 복사 해두고 다른 사람한테 알리지 않기

## 실행 방법
1. radio.py 파일을 실행하기
2. "첫 실행시" 필수 라이브러리가 설치되므로 기다려주세요
    1. 실패시 다음의 라이브러리를 수동으로 설치해주세요
    2. discord, discord.py, PyNaCl, eyeD3
3. "첫 실행시" 토큰을 입력합니다

## 명령어
- ;help : 도움말을 확인함

## 파일 추가 설명
- radio.py
    - 봇 핵심 파일
- option.py
    - 설정 파일
- option_editer.py
    - 설정파일 수정기
- data/lib/*
    - 자체 모듈 (수정 비권장)
- data/command/*
    - 명령어 모듈
