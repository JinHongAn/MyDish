from flask import Flask, request, jsonify
from sqlalchemy import text
from db import engine
import uuid
import random
from flask_cors import CORS
from recommend import recipe_df, recommend, get_user_likes, ingredient_vocab, RecipeRecommender, model, train_model_with_feedback
from recommend import train_model

from dotenv import load_dotenv
import os

load_dotenv()  # .env 파일의 환경변수를 로드

DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_NAME = os.getenv('DB_NAME')

app = Flask(__name__)
CORS(app)

model = RecipeRecommender(len(ingredient_vocab))
train_model(recipe_df, model, ingredient_vocab)

@app.route("/")
def home():
    return "Flask API is running!"


# ✅ 회원가입
@app.route("/api/signup", methods=["POST"])
def signup():
    data = request.json
    username = data.get("username")
    password = data.get("password")
    allergy = data.get("allergy", "")
    height = data.get("height_cm")
    weight = data.get("weight_kg")
    goal = data.get("goal", "maintain")
    user_id = str(uuid.uuid4())

    with engine.begin() as conn:
        check = conn.execute(text("SELECT * FROM user WHERE username = :u"), {"u": username}).fetchone()
        if check:
            return jsonify({"success": False, "message": "이미 존재하는 사용자입니다."}), 400

        conn.execute(text("""
            INSERT INTO user (user_id, username, password, allergy, height_cm, weight_kg, goal)
            VALUES (:id, :u, :p, :a, :h, :w, :g)
        """), {
            "id": user_id, "u": username, "p": password,
            "a": allergy, "h": height, "w": weight, "g": goal
        })

    return jsonify({"success": True, "message": "회원가입 완료", "user_id": user_id})


# ✅ 로그인
@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    with engine.begin() as conn:
        result = conn.execute(text("SELECT * FROM user WHERE username = :u AND password = :p"),
                              {"u": username, "p": password})
        user = result.mappings().fetchone()
        if user:
            return jsonify({"success": True, "user_id": user["user_id"]})
        else:
            return jsonify({"success": False, "message": "아이디 또는 비밀번호가 올바르지 않습니다."}), 401


# ✅ 레시피 추천
@app.route('/api/recommend', methods=['POST'])
def recommend_recipes():
    data = request.get_json()
    user_id = data.get('user_id')
    user_ingredients = data.get('ingredients', [])

    if not user_id or not user_ingredients:
        return jsonify({'error': '입력값 부족'}), 400

    try:
        with engine.connect() as conn:
            allergy_row = conn.execute(
                text("SELECT allergy FROM user WHERE user_id = :uid"),
                {'uid': user_id}
            ).fetchone()

        allergy_list = allergy_row[0].split(',') if allergy_row and allergy_row[0] else []
        likes = get_user_likes(user_id)

        results = recommend(model, user_ingredients, recipe_df, likes=likes, allergies=allergy_list, topk=10)
        return jsonify(results)

    except Exception as e:
        print("[ERROR] 추천 실패:", e)
        return jsonify({'error': '서버 오류'}), 500


# ✅ 즐겨찾기 / 피드백 저장
@app.route('/api/feedback', methods=['POST'])
def feedback():
    data = request.get_json()
    user_id = data.get('user_id')
    recipe_id = data.get('recipe_id')
    liked = data.get('liked', True)

    if not user_id or not recipe_id:
        return jsonify({'success': False, 'message': 'user_id 또는 recipe_id 누락'}), 400

    try:
        with engine.begin() as conn:
            conn.execute(text("""
                INSERT INTO Recommendation (
                    recommendation_id, history_id, rcm_user_id, rcm_recipe_id, user_feedback
                ) VALUES (:rid, :hid, :uid, :rcp, :fb)
            """), {
                'rid': random.randint(100000, 999999),
                'hid': random.randint(100000, 999999),
                'uid': user_id,
                'rcp': recipe_id,
                'fb': 'like' if liked else 'dislike'
            })

        # ✅ 사용자 피드백을 기반으로 모델 재학습 호출
        train_model_with_feedback(recipe_df, model, ingredient_vocab, user_id)

        return jsonify({'success': True})
    except Exception as e:
        print("[ERROR] 피드백 저장 실패:", e)
        return jsonify({'success': False, 'error': str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
