from flask import Flask, jsonify, request
import mysql.connector
from flask_cors import CORS
from datetime import datetime
import random
import numpy as np
from sklearn.model_selection import train_test_split
from tensorflow import keras
from tensorflow.keras import layers

app = Flask(__name__)
CORS(app)

# 配置数据库连接
db_config = {
    'user': 'root',
    'password': 'firefly@666',
    'host': 'localhost',
    'database': 'lottery_db',
    'charset': 'utf8mb4'
}

def get_db_connection():
    return mysql.connector.connect(**db_config)

@app.route('/api/history', methods=['GET'])
def get_history():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT draw_number, draw_date, numbers FROM history")
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    
    # 格式化日期和开奖号码
    for result in results:
        result['draw_date'] = result['draw_date'].strftime('%Y-%m-%d')
        
        # 处理开奖号码，确保只保留数字并用空格分隔
        # 假设numbers字段是以空格分隔的字符串
        numbers_list = result['numbers'].split()  # 分割字符串
        result['numbers'] = ' '.join(numbers_list)  # 重新连接为字符串
        
    return jsonify(results)

@app.route('/api/predict', methods=['POST'])
def predict():
    # 这里可以调用预测算法
    data = request.json
    # 假设返回一个预测结果
    prediction_result = {"prediction": "预测结果"}
    return jsonify(prediction_result)

@app.route('/api/random_numbers', methods=['GET'])
def generate_random_numbers():
    # 随机生成6个红球号码（1-33）
    red_balls = random.sample(range(1, 34), 6)
    # 随机生成1个蓝球号码（1-16）
    blue_ball = random.choice(range(1, 17))
    
    # 将红球号码排序
    red_balls.sort()
    
    # 格式化红球和蓝球号码为两位数
    formatted_red_balls = [f"{num:02d}" for num in red_balls]  # 使用字符串格式化
    formatted_blue_ball = f"{blue_ball:02d}"  # 同样格式化蓝球号码
    
    # 返回结果
    return jsonify({
        'red_balls': formatted_red_balls,
        'blue_ball': formatted_blue_ball
    })

@app.route('/api/train_model', methods=['POST'])
def train_model():
    # 从数据库获取历史数据
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT numbers FROM history")
    results = cursor.fetchall()
    cursor.close()
    conn.close()

    # 准备数据
    X = []
    y = []
    for result in results:
        numbers = list(map(int, result[0].split()))  # 将字符串转换为整数列表
        if len(numbers) == 7:  # 确保有7个号码
            X.append(numbers[:6])  # 前6个红球作为特征
            y.append(numbers[6])  # 第7个蓝球作为目标

    X = np.array(X)
    y = np.array(y)

    # 划分训练集和测试集
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # 创建模型
    model = keras.Sequential([
        layers.Dense(64, activation='relu', input_shape=(6,)),  # 输入层
        layers.Dense(64, activation='relu'),  # 隐藏层
        layers.Dense(1)  # 输出层
    ])

    model.compile(optimizer='adam', loss='mean_squared_error')

    # 训练模型
    model.fit(X_train, y_train, epochs=100, batch_size=32, validation_split=0.2)

    # 保存模型
    try:
        model.save('D:\cursor\project\redblueball\lottery_model.h5')
    except Exception as e:
        print(f"保存模型时出错: {e}")

    return jsonify({"message": "模型训练完成并保存！"})

@app.route('/api/predict_next', methods=['POST'])
def predict_next():
    # 获取输入数据
    data = request.json
    user_input = data.get('input_number')  # 获取用户输入的数字

    # 随机生成6个红球号码（1-33）
    red_balls = random.sample(range(1, 34), 6)
    # 随机生成1个蓝球号码（1-16）
    blue_ball = random.choice(range(1, 17))

    # 将红球号码排序
    red_balls.sort()

    # 返回完整的双色球号码
    return jsonify({
        "red_balls": red_balls,  # 返回生成的红球
        "blue_ball": blue_ball  # 返回生成的蓝球
    })

if __name__ == '__main__':
    app.run(debug=True) 