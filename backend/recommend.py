import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
from urllib.parse import quote_plus
from sqlalchemy import create_engine, text
import random
import uuid
import re
import math

# DB 연결
from dotenv import load_dotenv
import os

load_dotenv()  # .env 파일의 환경변수를 로드

DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_NAME = os.getenv('DB_NAME')

engine = create_engine(f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}?charset=utf8mb4')

# 레시피 불러오기
recipe_df = pd.read_sql("""
    SELECT recipe_id, CKG_NM, CKG_MTRL_ACTO_NM, RCP_PARTS_DTLS, INFO_ENG, INFO_NA, INFO_PRO, INFO_FAT, INFO_CAR,
           MANUAL01, MANUAL02, MANUAL03, MANUAL04, MANUAL05, MANUAL06
    FROM Recipe
""", engine)

def normalize_ingredient_string(raw_text):
    if not raw_text:
        return []

    text = raw_text.replace('\n', ',').lower()
    text = re.sub(r'[?★•▶◇■□※]+', '', text)
    text = re.sub(r'(필수\s?재료|양념|육수재료|육수)\s*:', '', text)
    text = re.sub(r'\([^)]*\)', '', text)

    # ✅ 여기서부터 수정
    text = re.sub(r'(\d+(\.\d+)?)(g|ml|kg|개|스푼|컵|큰술|작은술)?', '', text)  # 숫자+단위 제거
    # 숫자만 제거하는 부분 제거 (중복)
    # text = re.sub(r'\d+(\.\d+)?', '', text) ← 제거

    text = re.sub(r'[^가-힣a-zA-Z,]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()

    candidates = [i.strip() for i in text.split(',') if i.strip()]
    return candidates

# 재료 전처리
def extract_ingredients(text):
    return normalize_ingredient_string(text)

recipe_df['ingredient_list'] = recipe_df['RCP_PARTS_DTLS'].apply(extract_ingredients)

all_ingredients = sorted(set(i for lst in recipe_df['ingredient_list'] for i in lst))
ingredient_vocab = {ingredient: idx for idx, ingredient in enumerate(all_ingredients)}
vocab_size = len(ingredient_vocab)


def ingredients_to_indices(ingredients):
    return [ingredient_vocab[i] for i in ingredients if i in ingredient_vocab]

def pad_sequences(sequences, max_len=None, pad_value=0):
    if max_len is None:
        max_len = max(len(seq) for seq in sequences)
    return torch.tensor([seq + [pad_value]*(max_len - len(seq)) for seq in sequences], dtype=torch.long)

class RecipeRecommender(nn.Module):
    def __init__(self, vocab_size, embed_dim=64):
        super().__init__()
        self.user_embedding = nn.Embedding(vocab_size, embed_dim)
        self.recipe_embedding = nn.Embedding(vocab_size, embed_dim)
        self.fc = nn.Sequential(
            nn.Linear(embed_dim * 2, 128),
            nn.ReLU(),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Linear(64, 1)
        )

    def forward(self, user_ing, recipe_ing):
        user_emb = self.user_embedding(user_ing).mean(dim=1)
        recipe_emb = self.recipe_embedding(recipe_ing).mean(dim=1)
        x = torch.cat([user_emb, recipe_emb], dim=1)
        return self.fc(x).squeeze(1)


def calculate_bmr(weight, height, age=25, sex='M'):
    if sex == 'M':
        return 66.5 + 13.75 * weight + 5.003 * height - 6.755 * age
    else:
        return 655.1 + 9.563 * weight + 1.850 * height - 4.676 * age

def get_target_calories(bmr, goal):
    tdee = bmr * 1.2  # 활동량 낮음 기준
    if goal == 'loss':
        return tdee - 500
    elif goal == 'gain':
        return tdee + 500
    else:
        return tdee

def get_or_create_user(username, password, allergy):
    with engine.begin() as conn:
        result = conn.execute(text("SELECT * FROM user WHERE username = :u"), {"u": username})
        row = result.mappings().fetchone()
        if row:
            height = row["height_cm"]
            weight = row["weight_kg"]
            goal = row.get("goal", "maintain") if "goal" in row else "maintain"
            # height 또는 weight 가 None 이면 사용자에게 입력받아서 DB 업데이트
            if height is None:
                height = float(input("키(cm)를 입력하세요: "))
            if weight is None:
                weight = float(input("체중(kg)을 입력하세요: "))
            if (row["height_cm"] is None) or (row["weight_kg"] is None):
                # 업데이트
                conn.execute(text("""
                    UPDATE user SET height_cm = :h, weight_kg = :w WHERE user_id = :id
                """), {"h": height, "w": weight, "id": row["user_id"]})
            print(f"{username}님 환영합니다.")
            return row["user_id"], row["allergy"], height, weight, goal
        
        # 새 사용자 등록
        height = float(input("키(cm)를 입력하세요: "))
        weight = float(input("체중(kg)을 입력하세요: "))
        goal = input("목표를 입력하세요 (loss/maintain/gain): ").strip().lower()
        user_id = str(uuid.uuid4())
        conn.execute(text("""
            INSERT INTO user (user_id, username, password, allergy, height_cm, weight_kg)
            VALUES (:id, :u, :p, :a, :h, :w)
        """), {
            "id": user_id, "u": username, "p": password, "a": allergy,
            "h": height, "w": weight
        })
        print(f"{username}님이 새로 등록되었습니다.")
        return user_id, allergy, height, weight, goal


def train_model(df, model, ingredient_vocab, epochs=10, lr=0.001):
    optimizer = optim.Adam(model.parameters(), lr=lr)
    criterion = nn.BCEWithLogitsLoss()
    model.train()

    for epoch in range(epochs):
        total_loss = 0.0
        count = 0
        for i in range(len(df)):
            recipe_ing = ingredients_to_indices(df.iloc[i]['ingredient_list'])
            if not recipe_ing or len(recipe_ing) < 2:
                continue

            # 이전 학습: 같은 레시피의 일부 재료 → 사용자 재료로 사용
            # 현재 학습: 사용자 피드백 기반 좋아요한 재료 사용 (다음에 통합)
            # 아래에서 user_likes를 활용할 수 있게 구조만 유지
            user_ing = random.sample(recipe_ing, max(1, len(recipe_ing)//2))
            neg_ing = random.sample(
                list(set(range(vocab_size)) - set(recipe_ing)),
                len(user_ing)
            )

            user_tensor = pad_sequences([user_ing])
            recipe_tensor = pad_sequences([recipe_ing])
            neg_tensor = pad_sequences([neg_ing])

            optimizer.zero_grad()
            pos_score = model(user_tensor, recipe_tensor)
            neg_score = model(user_tensor, neg_tensor)

            label_pos = torch.ones_like(pos_score)
            label_neg = torch.zeros_like(neg_score)

            loss = criterion(pos_score, label_pos) + criterion(neg_score, label_neg)
            loss.backward()
            optimizer.step()

            total_loss += loss.item()
            count += 1

        avg_loss = total_loss / count if count else 0
        print(f"Epoch {epoch+1}, Avg Loss: {avg_loss:.4f}")

def train_model_with_feedback(df, model, ingredient_vocab, user_id, epochs=5, lr=0.001):
    print(f"\n📘 사용자 피드백 기반으로 모델 재학습 시작 (user_id: {user_id})")
    optimizer = optim.Adam(model.parameters(), lr=lr)
    criterion = nn.BCEWithLogitsLoss()
    model.train()

    # 1. 사용자 좋아요 레시피 기반 재료 수집
    user_likes = get_user_likes(user_id)
    user_ing = ingredients_to_indices(user_likes)
    if not user_ing:
        print("사용자의 좋아요 재료가 없어 일반 학습으로 대체합니다.")
        return train_model(df, model, ingredient_vocab, epochs, lr)

    user_tensor = pad_sequences([user_ing])

    for epoch in range(epochs):
        total_loss = 0.0
        count = 0
        for i in range(len(df)):
            recipe_ing = ingredients_to_indices(df.iloc[i]['ingredient_list'])
            if not recipe_ing:
                continue

            recipe_tensor = pad_sequences([recipe_ing])
            neg_ing = random.sample(
                list(set(range(vocab_size)) - set(recipe_ing)),
                min(len(recipe_ing), len(user_ing))
            )
            neg_tensor = pad_sequences([neg_ing])

            optimizer.zero_grad()
            pos_score = model(user_tensor, recipe_tensor)
            neg_score = model(user_tensor, neg_tensor)

            label_pos = torch.ones_like(pos_score)
            label_neg = torch.zeros_like(neg_score)

            loss = criterion(pos_score, label_pos) + criterion(neg_score, label_neg)
            loss.backward()
            optimizer.step()

            total_loss += loss.item()
            count += 1

        avg_loss = total_loss / count if count else 0
        print(f"Epoch {epoch+1}, Avg Loss: {avg_loss:.4f}")



def contains_allergy(ingredients, allergies):
    # 정규화된 소문자 단어 집합 생성
    norm_ingredients = set(i.strip().lower() for i in ingredients)
    norm_allergies = set(a.strip().lower() for a in allergies)
    return bool(norm_ingredients & norm_allergies)


def recommend(model, user_ingredients, df, likes=[], allergies=[], topk=10, calorie_limit=None, goal='maintain'):
    model.eval()
    with torch.no_grad():
        user_idx = ingredients_to_indices(user_ingredients)
        if not user_idx:
            print("사용자의 재료가 모두 사전에 없습니다.")
            return []

        user_tensor = pad_sequences([user_idx])
        scores = []

        norm_allergies = set(a.strip().lower() for a in allergies if a.strip())
        norm_user_ing = set(i.lower() for i in user_ingredients)
        norm_likes = set(i.lower() for i in likes)

        for i, row in df.iterrows():
            ing_list = row['ingredient_list']
            if not ing_list:
                scores.append(-float('inf'))
                continue

            if norm_allergies.intersection(i.lower() for i in ing_list):
                scores.append(-float('inf'))
                continue

            recipe_idx = ingredients_to_indices(ing_list)
            if not recipe_idx:
                scores.append(-float('inf'))
                continue

            recipe_tensor = pad_sequences([recipe_idx])

            # 모델 점수
            raw_score = model(user_tensor, recipe_tensor).item()
            prob_score = torch.sigmoid(torch.tensor(raw_score)).item()

            # 가중치 기반 점수 계산
            matched_user = len(set(i.lower() for i in ing_list) & norm_user_ing)
            matched_like = len(set(i.lower() for i in ing_list) & norm_likes)

            # 사용자 재료 가중치 ↑
            score = 1.5 * matched_user + 0.1 * matched_like + 0.5 * prob_score

            # 칼로리 페널티 적용
            cal = row.get('INFO_ENG', 0) or 0
            if calorie_limit is not None:
                if goal == 'loss' and cal > calorie_limit:
                    score -= (cal - calorie_limit) / 500.0
                elif goal == 'gain' and cal < calorie_limit:
                    score -= (calorie_limit - cal) / 500.0
                elif goal == 'maintain' and abs(cal - calorie_limit) > 200:
                    score -= abs(cal - calorie_limit) / 500.0

            scores.append(score)

        top_indices = sorted(
            [i for i, s in enumerate(scores) if s != -float('inf')],
            key=lambda x: scores[x],
            reverse=True
        )[:topk]

        recs = []
        for idx in top_indices:
            rec = df.iloc[idx]
            missing = [i for i in rec['ingredient_list'] if i.lower() not in norm_user_ing]
            recs.append({
                'recipe_id': int(rec['recipe_id']),
                'recipe_name': rec['CKG_NM'],
                'ingredients': rec['RCP_PARTS_DTLS'],
                'missing_ingredients': ', '.join(missing) if missing else '없음',
                'score': round(scores[idx], 4),
                'calories': rec.get('INFO_ENG', 'N/A'),
                'MANUAL01': rec.get('MANUAL01', ''),
                'MANUAL02': rec.get('MANUAL02', ''),
                'MANUAL03': rec.get('MANUAL03', ''),
                'MANUAL04': rec.get('MANUAL04', ''),
                'MANUAL05': rec.get('MANUAL05', ''),
                'MANUAL06': rec.get('MANUAL06', ''),
                'INFO_NA': rec.get('INFO_NA', 0),
                'INFO_PRO': rec.get('INFO_PRO', 0),
                'INFO_FAT': rec.get('INFO_FAT', 0),
                'INFO_CAR': rec.get('INFO_CAR', 0),
                'INFO_ENG': rec.get('INFO_ENG', 0)
})
        return recs

def log_recommendation(user_id, recipe_id, liked):
    with engine.begin() as conn:
        conn.execute(text("""
            INSERT INTO Recommendation (recommendation_id, history_id, rcm_user_id, rcm_recipe_id, user_feedback)
            VALUES (:rid, :hid, :uid, :rcp, :fb)
        """), {
            "rid": random.randint(100000, 999999),
            "hid": random.randint(100000, 999999),
            "uid": user_id,
            "rcp": recipe_id,
            "fb": 'like' if liked else 'dislike'
        })

def get_user_likes(user_id):
    query = """
    SELECT r.RCP_PARTS_DTLS
    FROM Recommendation rec
    JOIN Recipe r ON rec.rcm_recipe_id = r.recipe_id
    WHERE rec.rcm_user_id = :uid AND rec.user_feedback = 'like'
    """
    df = pd.read_sql(text(query), engine, params={"uid": user_id})
    like_ingredients = []
    for s in df['RCP_PARTS_DTLS']:
        like_ingredients += extract_ingredients(s)
    return like_ingredients




# 실행
if __name__ == '__main__':
    username = input("사용자 이름 입력: ")
    password = input("비밀번호 입력: ")

    user_id, allergy_db, height, weight, goal = get_or_create_user(username, password, "")

    allergy_list = [x.strip() for x in allergy_db.split(',')] if allergy_db else []

    bmr = calculate_bmr(weight, height)
    calorie_limit = get_target_calories(bmr, goal)
    print(f"\n사용자의 일일 권장 섭취 칼로리: {round(calorie_limit)} kcal")

    fridge_input = input("냉장고 재료 (쉼표로 구분): ")
    fridge_ingredients = [x.strip() for x in fridge_input.split(',') if x.strip()]

    likes_from_history = get_user_likes(user_id)

    # 모델 생성 및 학습 호출를 여기로 옮김
    model = RecipeRecommender(vocab_size)
    train_model_with_feedback(recipe_df, model, ingredient_vocab, user_id)

    recs = recommend(
        model,
        fridge_ingredients,
        recipe_df,
        likes=likes_from_history,
        allergies=allergy_list,
        topk=10,
        calorie_limit=calorie_limit
    )

    if not recs:
        print("추천 가능한 요리가 없습니다. 재료나 알러지를 다시 확인해 주세요.")
    else:
        print("\n추천 요리:")
        for i, r in enumerate(recs):
            print(f"{i+1}. {r['recipe_name']} (점수: {r['score']}, 칼로리: {r['calories']} kcal)")
            print(f"   필요한 재료: {r['ingredients']}")
            print(f"   부족한 재료: {r['missing_ingredients']}")
        choice = input("좋아하는 레시피 번호 입력 (건너뛰려면 Enter): ")
        if choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(recs):
                log_recommendation(user_id, recs[idx]['recipe_id'], liked=True)
                print(f"{recs[idx]['recipe_name']}을(를) 좋아함으로 기록했습니다.")

model = RecipeRecommender(vocab_size)
train_model(recipe_df, model, ingredient_vocab)

    
