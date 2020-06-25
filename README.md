# RadioBOT
discord.py를 사용해서 만든 디스코드 라디오 봇

## 실행 전 설정
1. 음악 풀더에 음악 채우기 ( 기본위치: ./data/music/ )
    1. 또는 본인의 음악 풀더로 설정 수정하기
2. 디스코드 개발자 센터에서 자신의 봇 만들기
3. 토큰 복사 해두고 다른 사람한테 알리지 않기

## 실행 방법
1. radio.py 파일을 실행하기
2. "첫 실행시" 필수 라이브러리가 설치되므로 기다려주세요
    1. 실패시 다음의 라이브러리를 수동으로 설치해주세요
    2. discord, discord.py, PyNaCl, eyeD3
3. "첫 실행시" 토큰을 입력합니다

## 명령어
<pre>
;join &lt;or&gt; ;j
 -  라디오의 전원을 킵니다! (음성채널에 입장해야 합니다...)
;exit &lt;or&gt; ;e
 -  라디오의 전원을 끕니다...
;skip &lt;or&gt; ;s
 -  지금 재생되고 있는 노래를 넘깁니다
;nowplay &lt;or&gt; ;np
 -  지금 재생되는 음악의 정보를 확인합니다
;repeat &lt;or&gt; ;re
 -  반복재생 모드를 [활성화/비활성화] 합니다
 
;play &#91;&lt;트랙번호&gt;&#93; &lt;or&gt; ;p &#91;&lt;트랙번호&gt;&#93;
 -  다음에 재생할 노래를 지정합니다
;search &#91;&lt;검색어&gt;&#93; &lt;or&gt; ;sh &#91;&lt;검색어&gt;&#93;
 -  검색기능은 트랙번호 또는 작곡가 또는 제목으로 검색이 가능합니다
</pre>
### 봇 주인 전용 명령어
<pre>
;close
 -  봇을 끕니다
;leave_all
 -  작동중인 모든 라디오를 끕니다
 ;reload_playlist
 -  재생목록을 다시 불러옵니다 (모든 라디오가 종료됨)
</pre>

## 설정 파일
설정 파일을 수정하고 봇이 정상적으로 실행되지 않는다면
설정파일을 삭제해서 봇이 초기화 하도록 해주세요.
<pre>
&#91;봇 주인 자동 감지 (기본값: true)&#93;
auto_owner:(true/false)

&#91;봇 주인 id (기본값: 0)&#93;
owner_id: (int),

&#91;색깔 수정 비권장&#93;
"color": {
    "info": (int),
    "normal": (int),
    "warn": (int)
}

&#91;언어 파일 이름 (기본값: ko)
- 언어파일 저장 위치: ./data/i18n/&#91;&lt;언어명&gt;&#93;.json
lang": "&#91;&lt;언어명&gt;&#93;"

&#91;접두사 (기본값: ;)&#93;
prefix: "&#91;&lt;접두사&gt;&#93;"

&#91;보호모드 활성화 여부 (기본값: false)&#93;
private_mode: (true/false)

&#91;봇이 접속한 길드 저장 여부 (기본값: false)&#93;
save_guild_data: (true/false)

&#91;음악 인식풀더 (기본값: ./data/music/)&#93;
music_dir: "./data/music/"
</pre>