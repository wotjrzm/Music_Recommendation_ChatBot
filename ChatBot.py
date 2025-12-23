import os
import pandas as pd
from dotenv import load_dotenv
from openai import OpenAI

# 1. .env 파일에 저장된 환경 변수를 불러옵니다.
load_dotenv()

def run_emotion_chatbot():
    # 2. os.getenv를 통해 보안 환경 변수에서 키를 가져옵니다.
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        print("에러: API 키를 찾을 수 없습니다. .env 파일을 확인해주세요.")
        return None, None

    client = OpenAI(api_key=api_key)

    user_name = input("Enter your name: ").strip()
    print(f'\n<{user_name}>')

    messages = []
    
    # 초기 페르소나 설정
    system_content = (
        "너는 사용자의 이야기를 경청하고 공감해주는 따뜻한 대화 친구야. "
        "사용자가 어떤 이야기를 하든 친절하고 자연스럽게 대화를 이어가줘. "
        "대화가 충분히 진행되었거나 사용자가 추천을 원할 때까지는 계속 대화해."
    )
    messages.append({"role": "system", "content": system_content})

    print(f"GPT : 안녕하세요, {user_name}님! 오늘 하루는 어떠셨나요? (대화를 끝내고 싶으면 '추천'이나 '그만'이라고 말해주세요)")

    # 자유 대화 루프
    while True:
        user_input = input("User : ").strip()
        
        if any(keyword in user_input for keyword in ['추천', '그만', '종료', '노래', 'music']):
            print("\nGPT : 네, 그럼 지금까지의 대화를 바탕으로 감정을 분석하고 노래를 추천해드릴게요.\n")
            break
            
        messages.append({"role": "user", "content": user_input})
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages
        )
        assistant_reply = response.choices[0].message.content.strip()
        print(f"GPT : {assistant_reply}")
        messages.append({"role": "assistant", "content": assistant_reply})

    # 감정 분석 단계
    analysis_prompt = (
        "지금까지의 대화 내용을 바탕으로 사용자의 현재 핵심 감정을 다음 중 하나로만 딱 골라서 대답해줘. "
        "다른 말은 붙이지 말고 오직 단어 하나만 말해.\n"
        "목록: [사랑, 즐거움, 열정, 행복, 슬픔, 분노, 외로움, 그리움, 두려움]"
    )
    messages.append({"role": "system", "content": analysis_prompt})
    
    analysis_response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages
    )
    
    emotion = analysis_response.choices[0].message.content.strip()

    # 특수문자 제거 가공
    for char in ["[", "]", "'", '"', ".", " "]:
        emotion = emotion.replace(char, "")
    
    print(f"{user_name}'s emotion : {emotion}")
    return user_name, emotion


def get_songs_by_emotion(emotion, csv_path):
    try:
        # 파일 존재 여부 확인
        if not os.path.exists(csv_path):
            print(f"에러: CSV 파일을 찾을 수 없습니다. 경로를 확인하세요: {csv_path}")
            return []

        df = pd.read_csv(csv_path)
        required_columns = {'emotion1', 'singer', 'title', 'genre'}
        
        if not required_columns.issubset(df.columns):
            print(f"에러: CSV에 필요한 컬럼이 없습니다: {required_columns}")
            return []

        # 감정 기준 필터링 (공백 제거 후 비교)
        filtered = df[df['emotion1'].astype(str).str.strip() == emotion]
        return filtered[['singer', 'title', 'genre']].to_dict(orient='records')

    except Exception as e:
        print(f"에러 발생: {e}")
        return []


if __name__ == "__main__":
    # 데이터 경로 설정 (상대 경로 사용 권장)
    CSV_FILE_PATH = 'data/Final_lyrics_emotion_analysis.csv'

    # 챗봇 실행 및 결과 받기
    user_name, emotion = run_emotion_chatbot()
    
    if emotion:
        mapping_songs = get_songs_by_emotion(emotion, CSV_FILE_PATH)

        print(f"\n추천 노래 리스트 ({emotion} 감정 기반):")
        if not mapping_songs:
            print("일치하는 감정의 노래를 찾지 못했습니다.")
        else:
            for song in mapping_songs:
                print(f"- {song['singer']} : {song['title']} [{song['genre']}]")