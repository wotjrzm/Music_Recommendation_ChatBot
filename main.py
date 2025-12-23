import os
import pandas as pd
from lyrics_emotion_analysis_KR import hybrid_emotion_analysis, load_vocab, load_model

# 경로 설정
data_path = 'data/lyrics_by_year_1964_2023.csv'
vocab_path = 'data/vocab_9class_500.csv'
stopwords_path = 'data/stopwords.txt'
model_checkpoint_path = os.path.join("model", "tf2_bert_sentiment", "best_model")

# 데이터 불러오기
df = pd.read_csv(data_path)

# 감정 어휘 사전 불러오기
vocab = load_vocab(vocab_path, stopwords_path)

# 학습된 모델 불러오기
model = load_model(model_checkpoint_path)

# 감정 분석 수행
emotion_labels = df['lyric'].apply(lambda x: hybrid_emotion_analysis(x, model, vocab))

# 결과를 컬럼으로 분리하여 저장
df[['emotion1', 'emotion2', 'emotion3']] = pd.DataFrame(emotion_labels.tolist(), index=df.index)

# 파일 저장
output_path = 'data/Final_lyrics_emotion_analysis.csv'
df.to_csv(output_path, index=False, encoding='utf-8-sig')

print(f"감정 분석 완료: '{output_path}'로 저장됨.")