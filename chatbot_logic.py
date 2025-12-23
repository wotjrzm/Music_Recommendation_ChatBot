import os
import pandas as pd
from dotenv import load_dotenv
from openai import OpenAI

# .env 파일 로드
load_dotenv()

class EmotionChatBot:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("API Key not found in .env file.")
        
        self.client = OpenAI(api_key=self.api_key)
        self.messages = []
        self._initialize_system_prompt()
        self.user_name = "User" # Default

    def _initialize_system_prompt(self):
        system_content = (
            "너는 사용자의 이야기를 경청하고 공감해주는 따뜻한 대화 친구야. "
            "사용자가 어떤 이야기를 하든 친절하고 자연스럽게 대화를 이어가줘. "
            "대화가 충분히 진행되었거나 사용자가 추천을 원할 때까지는 계속 대화해."
        )
        self.messages.append({"role": "system", "content": system_content})

    def set_user_name(self, name):
        self.user_name = name

    def get_response(self, user_input):
        self.messages.append({"role": "user", "content": user_input})
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=self.messages
            )
            assistant_reply = response.choices[0].message.content.strip()
            self.messages.append({"role": "assistant", "content": assistant_reply})
            return assistant_reply
        except Exception as e:
            return f"오류가 발생했습니다: {str(e)}"

    def analyze_emotion(self):
        analysis_prompt = (
            "지금까지의 대화 내용을 바탕으로 사용자의 현재 핵심 감정을 다음 중 하나로만 딱 골라서 대답해줘. "
            "다른 말은 붙이지 말고 오직 단어 하나만 말해.\n"
            "목록: [사랑, 즐거움, 열정, 행복, 슬픔, 분노, 외로움, 그리움, 두려움]"
        )
        # 분석을 위한 임시 메시지 리스트 생성 (시스템 프롬프트 추가)
        analysis_messages = self.messages + [{"role": "system", "content": analysis_prompt}]
        
        try:
            analysis_response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=analysis_messages
            )
            emotion = analysis_response.choices[0].message.content.strip()
            
            # 특수문자 제거
            for char in ["[", "]", "'", '"', ".", " "]:
                emotion = emotion.replace(char, "")
                
            return emotion
        except Exception as e:
            print(f"Emotion Analysis Error: {e}")
            return None

def get_songs_by_emotion(emotion, csv_path='data/Final_lyrics_emotion_analysis.csv'):
    try:
        if not os.path.exists(csv_path):
            # 절대 경로로 시도하거나, 상위 디렉토리 확인 등 예외 처리 강화 가능
            print(f"File not found: {csv_path}")
            return []

        df = pd.read_csv(csv_path)
        required_columns = {'emotion1', 'singer', 'title', 'genre'}
        
        if not required_columns.issubset(df.columns):
            print(f"Missing columns. Required: {required_columns}")
            return []

        # 감정 기준 필터링
        filtered = df[df['emotion1'].astype(str).str.strip() == emotion]
        
        # 결과가 너무 많으면 랜덤으로 5개만 추천하는 등의 로직 추가 가능하지만, 일단 전체 반환
        return filtered[['singer', 'title', 'genre']].to_dict(orient='records')

    except Exception as e:
        print(f"Error reading CSV: {e}")
        return []
