import pandas as pd
import mysql.connector
import math

csv_file = 'recipes(1_1000).csv'

df = pd.read_csv(csv_file, encoding='cp949')

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="zoqtmxhs12!",
    database="mydish_db"
)

cursor = conn.cursor()

def clean_val(val):
    # NaN 또는 빈 문자열일 경우 None 리턴
    if pd.isna(val):
        return None
    if isinstance(val, (int, float)):
        if math.isnan(val):
            return None
        return val
    if isinstance(val, str) and val.strip() == '':
        return None
    return val

for _, row in df.iterrows():
    try:
        recipe_id = int(row['RCP_SNO'])
    except (ValueError, TypeError):
        recipe_id = None

    sql = """
    INSERT IGNORE INTO Recipe (
        recipe_id, CKG_NM, CKG_MTH_ACTO_NM, CKG_MTRL_ACTO_NM, CKG_KND_ACTO_NM,
        CKG_TIME_NM, RCP_PARTS_DTLS, INFO_NA, INFO_PRO, INFO_FAT,
        INFO_CAR, INFO_ENG, RCP_NA_TIP, MANUAL01, MANUAL02,
        MANUAL03, MANUAL04, MANUAL05, MANUAL06
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    values = (
        recipe_id,
        clean_val(row['CKG_NM']),
        clean_val(row['CKG_MTH_ACTO_NM']),
        clean_val(row['CKG_MTRL_ACTO_NM']),
        clean_val(row['CKG_KND_ACTO_NM']),
        clean_val(row['CKG_TIME_NM']),
        clean_val(row['RCP_PARTS_DTLS']),
        clean_val(row['INFO_NA']),
        clean_val(row['INFO_PRO']),
        clean_val(row['INFO_FAT']),
        clean_val(row['INFO_CAR']),
        clean_val(row['INFO_ENG']),
        clean_val(row['RCP_NA_TIP']),
        clean_val(row['MANUAL01']),
        clean_val(row['MANUAL02']),
        clean_val(row['MANUAL03']),
        clean_val(row['MANUAL04']),
        clean_val(row['MANUAL05']),
        clean_val(row['MANUAL06']),
    )
    cursor.execute(sql, values)

conn.commit()
cursor.close()
conn.close()

print("✅ CSV 데이터를 MySQL로 성공적으로 삽입했습니다.")
