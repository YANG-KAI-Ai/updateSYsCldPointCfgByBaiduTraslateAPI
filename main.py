import pandas as pd
import mysql.connector
import re
import time
import requests
import hashlib
import random
from sqlalchemy import create_engine

# 百度翻译 API 信息
appid = ''  # 你的百度翻译API的appid
secretKey = ''  # 你的密钥

def baidu_translate_batch(queries, from_lang='zh', to_lang='en'):
    base_url = 'http://api.fanyi.baidu.com/api/trans/vip/translate'
    salt = str(random.randint(32768, 65536))
    query_str = '\n'.join(queries)
    sign = appid + query_str + salt + secretKey
    sign = hashlib.md5(sign.encode()).hexdigest()
    params = {
        'q': query_str,
        'from': from_lang,
        'to': to_lang,
        'appid': appid,
        'salt': salt,
        'sign': sign
    }
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        result = response.json()
        if 'trans_result' in result:
            translations = result['trans_result']
            return [item['dst'] for item in translations]
        else:
            print(f"Error translating batch: {queries}, error: {result}")
            return ['translation_error'] * len(queries)
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return ['translation_error'] * len(queries)
    except ValueError as e:
        print(f"Error parsing JSON: {e}")
        print(f"Response content: {response.text}")
        return ['translation_error'] * len(queries)

def format_field_name(translation):
    # 删除特殊字符并限制长度
    translation = re.sub(r'[^\w\s]', '', translation)  # 去掉所有特殊字符
    words = translation.split()
    shortened_words = [word[:3] for word in words]  # 取每个单词的前三个字母
    return '_'.join(shortened_words).lower()

# 建立数据库连接，使用 SQLAlchemy
engine = create_engine('mysql+mysqlconnector://root:Yuyou123@db.yuyouship.top:3306/yuyou_shore_top')

# 读取数据
query = "SELECT * FROM sys_cld_point_cfg"
df = pd.read_sql(query, engine)

# 打印列名，检查是否有 'comment'
print(df.columns)

# 去除comment中的数字
def normalize_comment(comment):
    return re.sub(r'\d号', '', comment)

# 归一化comment
df['normalized_comment'] = df['comment'].apply(normalize_comment)

# 获取需要翻译的唯一归一化comment
unique_comments = df['normalized_comment'].unique()

# 分批进行翻译，避免一次性翻译数量过多
batch_size = 50
translated_comments = []

for i in range(0, len(unique_comments), batch_size):
    batch = unique_comments[i:i+batch_size]
    translations = baidu_translate_batch(batch)
    translated_comments.extend(translations)
    time.sleep(1)  # 等待一秒再进行下一次请求

# 创建一个字典来存储相同normalized_comment的field_name
field_name_mapping = {}
for comment, translation in zip(unique_comments, translated_comments):
    formatted_translation = format_field_name(translation)
    field_name_mapping[comment] = formatted_translation
    print(f"{comment} -> {formatted_translation}")

# 更新field_name为空、空字符或只有空格的字段
for index, row in df.iterrows():
    if pd.isnull(row['field_name']) or row['field_name'].strip() == '':
        norm_comment = row['normalized_comment']
        df.at[index, 'field_name'] = field_name_mapping.get(norm_comment, 'translation_error')

# 将数据写回数据库
conn = mysql.connector.connect(
    host='db.yuyouship.top',
    port=3306,  # 如果不是默认端口，请替换为实际端口
    user='root',
    password='Yuyou123',
    database='yuyou_shore_top'
)
cursor = conn.cursor()
for index, row in df.iterrows():
    update_query = """
    UPDATE sys_cld_point_cfg
    SET field_name = %s
    WHERE ID = %s
    """
    cursor.execute(update_query, (row['field_name'], row['ID']))
    conn.commit()

# 关闭数据库连接
conn.close()
