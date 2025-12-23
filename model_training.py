import os
import re
import numpy as np
from tqdm import tqdm

import tensorflow as tf
from transformers import *

from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint

import pandas as pd
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split

from lyrics_preprocessing import *
from lyrics_emotion_analysis_KR import *

#random seed 고정
tf.random.set_seed(1234)
np.random.seed(1234)

BATCH_SIZE = 16
NUM_EPOCHS = 30
VALID_SPLIT = 0.3
MAX_LEN = 13

tokenizer = BertTokenizer.from_pretrained("bert-base-multilingual-cased", cache_dir='bert_ckpt', do_lower_case=False)

def get_sentiment(emotion):
    if emotion == 0:
        return None
    # 긍정적인 감정은 1로 치환
    elif (emotion == 1 or emotion == 2 or emotion == 3):
        return 1
    # 부정적인 감정은 0으로 치환
    elif (emotion == 4 or emotion == 5 or emotion == 6):
        return 0

# 데이터 불러오기
data = pd.read_excel('data/train_data.xlsx')

# 라벨링 된 데이터만 불러오기
data = data[data['sentiment'].notnull()]

# 긍/부정 치환
data['sentiment'] = data['sentiment'].map(lambda x : get_sentiment(x))

data = data[(data['sentiment'] == 1) | (data['sentiment'] == 0)]
data['sentiment'] = data['sentiment'].astype('int64')
data = data[['lyrics splited','sentiment']]

input_ids = []
attention_masks = []
token_type_ids = []
train_data_labels = []

for train_sent, train_label in tqdm(zip(data["lyrics splited"], data["sentiment"]), total=len(data)):
    try:
        input_id, attention_mask, token_type_id = bert_tokenizer(train_sent, MAX_LEN)

        input_ids.append(input_id)
        attention_masks.append(attention_mask)
        token_type_ids.append(token_type_id)
        train_data_labels.append(train_label)

    except Exception as e:
        print(e)
        print(train_sent)
        pass

train_movie_input_ids = np.array(input_ids, dtype=int)
train_movie_attention_masks = np.array(attention_masks, dtype=int)
train_movie_type_ids = np.array(token_type_ids, dtype=int)
train_movie_inputs = (train_movie_input_ids, train_movie_attention_masks, train_movie_type_ids)

train_data_labels = np.asarray(train_data_labels, dtype=np.int32)  # 레이블 토크나이징 리스트

print("# sents: {}, # labels: {}".format(len(train_movie_input_ids), len(train_data_labels)))


sentiment_model = TFBertClassifier(model_name='bert-base-multilingual-cased',
                                  dir_path='bert_ckpt')


import tensorflow_addons as tfa
# 총 batch size * 4 epoch = 2344 * 4
opt = tfa.optimizers.RectifiedAdam(lr=5.0e-5, total_steps = 2344*2, warmup_proportion=0.1, min_lr=1e-5, epsilon=1e-08, clipnorm=1.0)
loss = tf.keras.losses.BinaryCrossentropy(from_logits=True)
sentiment_model.compile(optimizer=opt, loss=loss, metrics=['accuracy'])

model_name = "tf2_bert_sentiment"

# overfitting을 막기 위한 ealrystop 추가
earlystop_callback = EarlyStopping(monitor='val_accuracy', min_delta=0.0001, patience=3)
# min_delta: the threshold that triggers the termination (acc should at least improve 0.0001)
# patience: no improvment epochs (patience = 1, 1번 이상 상승이 없으면 종료)

checkpoint_path = os.path.join("model/", model_name, 'best_model')
checkpoint_dir = os.path.dirname(checkpoint_path)

# Create path if exists
if os.path.exists(checkpoint_dir):
    print("{} -- Folder already exists \n".format(checkpoint_dir))
else:
    os.makedirs(checkpoint_dir, exist_ok=True)
    print("{} -- Folder create complete \n".format(checkpoint_dir))

cp_callback = ModelCheckpoint(
    checkpoint_path, monitor='val_loss', verbose=1, mode='min', save_best_only=True, save_weight_only=True)

# 학습과 eval 시작
history = sentiment_model.fit(train_movie_inputs, train_data_labels, epochs=NUM_EPOCHS, batch_size=BATCH_SIZE,
                              validation_split=VALID_SPLIT, callbacks=[earlystop_callback, cp_callback])

# steps_for_epoch

print(history.history)