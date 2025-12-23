import streamlit as st
import time
from chatbot_logic import EmotionChatBot, get_songs_by_emotion

# 페이지 설정
st.set_page_config(page_title="감정 기반 음악 추천 봇", page_icon="🎵")

# 세션 상태 초기화
if "chatbot" not in st.session_state:
    try:
        st.session_state.chatbot = EmotionChatBot()
    except ValueError as e:
        st.error(f"초기화 오류: {e}")
        st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = []

if "chat_finished" not in st.session_state:
    st.session_state.chat_finished = False

if "emotion_result" not in st.session_state:
    st.session_state.emotion_result = None

# UI 헤더
st.title("🎵 감정 기반 음악 추천 챗봇")
st.markdown("당신의 이야기를 들려주세요. 감정에 맞는 음악을 추천해드립니다.")

# 채팅 히스토리 표시
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 사용자 입력 처리
if not st.session_state.chat_finished:
    if prompt := st.chat_input("오늘 하루는 어떠셨나요?"):
        # 사용자 메시지 표시
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # 챗봇 응답 생성
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            
            # 종료 키워드 감지
            if any(keyword in prompt for keyword in ['추천', '그만', '종료', '노래', 'music']):
                full_response = "네, 지금까지의 이야기를 바탕으로 음악을 추천해드릴게요. 잠시만 기다려주세요..."
                message_placeholder.markdown(full_response)
                st.session_state.messages.append({"role": "assistant", "content": full_response})
                st.session_state.chat_finished = True
                st.rerun() # 상태 업데이트를 위해 리런
            else:
                # 일반 대화 응답
                response_text = st.session_state.chatbot.get_response(prompt)
                
                # 스트리밍 효과 (선택 사항)
                for chunk in response_text.split():
                    full_response += chunk + " "
                    time.sleep(0.05)
                    message_placeholder.markdown(full_response + "▌")
                message_placeholder.markdown(full_response)
                
                # 내부 챗봇 객체 상태와 싱크 (이미 get_response에서 messages append 됨)
                st.session_state.messages.append({"role": "assistant", "content": full_response})

# 감정 분석 및 추천 결과 표시
if st.session_state.chat_finished:
    st.divider()
    with st.status("감정을 분석하고 있습니다...", expanded=True) as status:
        if not st.session_state.emotion_result:
            st.write("대화 내용을 분석 중입니다...")
            emotion = st.session_state.chatbot.analyze_emotion()
            st.session_state.emotion_result = emotion
            st.write(f"분석된 감정: **{emotion}**")
            status.update(label="분석 완료!", state="complete", expanded=False)
        else:
             status.update(label="분석 완료!", state="complete", expanded=False)

    if st.session_state.emotion_result:
        emotion = st.session_state.emotion_result
        st.success(f"당신의 현재 감정은 **[{emotion}]** 입니다.")
        
        st.subheader(f"🎧 {emotion}할 때 듣기 좋은 노래")
        
        songs = get_songs_by_emotion(emotion)
        
        if songs:
            for i, song in enumerate(songs[:5]): # 상위 5개만 표시
                st.markdown(f"**{i+1}. {song['title']}** - {song['singer']}")
                st.caption(f"장르: {song['genre']}")
        else:
            st.warning("추천할 노래를 찾지 못했습니다.")
            
    if st.button("다시 시작하기"):
        st.session_state.clear()
        st.rerun()
