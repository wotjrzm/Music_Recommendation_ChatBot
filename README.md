# 🎵 Emotion Based Music Recommendation Chatbot

사용자의 대화를 통해 현재 감정을 분석하고, 그 감정에 어울리는 음악을 추천해주는 챗봇 서비스입니다.

## 🌟 주요 기능
- **감성 대화**: 사용자와 자연스러운 대화를 나누며 '공감'하는 페르소나를 가집니다.
- **감정 분석**: 대화 내용을 바탕으로 9가지 핵심 감정(사랑, 즐거움, 슬픔 등) 중 하나를 분석합니다.
- **음악 추천**: 분석된 감정에 맞는 노래 리스트를 추천해줍니다.

## 🛠️ 기술 스택
- **Language**: Python 3.9+
- **AI/ML**: OpenAI GPT-3.5 Turbo (대화 및 감정 추론), KoBERT (학습 모델 활용 시)
- **Web Framework**: Streamlit
- **Data**: Melon 가사 데이터 (1964~2023)

## 🚀 실행 방법

### 1. 환경 설정
필요한 라이브러리를 설치합니다.
```bash
pip install -r requirements.txt
```

### 2. API 키 설정
`.env` 파일을 생성하고 OpenAI API 키를 입력해야 합니다.
```env
OPENAI_API_KEY=sk-your-api-key-here
```

### 3. 앱 실행
```bash
streamlit run app.py
```

## 📁 프로젝트 구조
- `app.py`: 웹 애플리케이션 메인 (Streamlit)
- `chatbot_logic.py`: 챗봇 핵심 로직 및 데이터 처리
- `main.py`: 데이터 전처리 및 분석 스크립트
- `model/`: 감정 분석 모델 저장소 (Git 제외)
- `data/`: 음악/가사 데이터셋
