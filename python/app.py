import os
from datetime import datetime, timedelta
import mysql.connector
from mysql.connector import pooling
from flask import Flask, request, jsonify, send_from_directory, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename
import uuid
import io
import xlsxwriter
import pandas as pd
from flask_jwt_extended import JWTManager, create_access_token, get_jwt_identity, jwt_required
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from io import BytesIO
from PIL import Image
from pathlib import Path
from functools import wraps
import time
# 导入返款系统路由
from routes import refund
from routes.refund import refund_bp  # 导入蓝图

app = Flask(__name__)
port = 3000
CORS(app)

# # CORS 配置
# cors_options = {
#     "origins": ["http://localhost:5173", "http://127.0.0.1:5173""http://192.168.1.20:5173""http://192.168.1.20:5000""http://192.168.1.20:5173""http://192.168.1.20:3000"],
#     "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
#     "allow_headers": [
#         "Content-Type",
#         "Accept",
#         "Authorization",
#         "X-Requested-With",
#         "X-Token",
#         "X-Username",
#         "X-Password"
#     ],
#     "expose_headers": [
#         "Content-Length",
#         "Content-Type",
#         "Authorization",
#         "X-Token"
#     ],
#     "supports_credentials": True
# }
# CORS(app, resources={
#     r"/api/*": cors_options,
#     r"/basic-api/*": cors_options,  # 添加 basic-api 路径的 CORS 配置
#     r"/uploads/*": cors_options     # 添加 uploads 路径的 CORS 配置
# })
# CORS 配置
cors_options = {
    "origins": [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://192.168.1.20:5173",  # 添加你的内网 IP
        "http://192.168.1.20:5000"   # 添加后端地址
    ],
    "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    "allow_headers": [
        "Content-Type",
        "Accept",
        "Authorization",
        "X-Requested-With",
        "X-Token",
        "X-Username",
        "X-Password",
        "Origin"  # 添加 Origin 头
    ],
    "expose_headers": [
        "Content-Length",
        "Content-Type",
        "Authorization",
        "X-Token"
    ],
    "supports_credentials": True,
    "allow_credentials": True,  # 添加这行
    "max_age": 3600  # 添加预检请求缓存时间
}

CORS(app, resources={
    r"/api/*": cors_options,
    r"/api/options": cors_options,
    r"/basic-api/*": cors_options,
    r"/uploads/*": cors_options
})

# 添加全局 CORS 处理
@app.after_request
def after_request(response):
    origin = request.headers.get('Origin')
    if origin in cors_options["origins"]:
        response.headers.add('Access-Control-Allow-Origin', origin)
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response
# 文件上传配置
BASE_DIR = Path(__file__).resolve().parent
UPLOAD_FOLDER = BASE_DIR / 'public' / 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
MAX_IMAGES_PER_REQUEST = 20
# 确保上传目录存在
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
app.config['UPLOAD_FOLDER'] = str(UPLOAD_FOLDER)
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
# 数据库配置
db_config = {
    "host": "localhost",
    "user": "test",
    "password": "test",
    "database": "assessment_business",
    "port": 3307,
    "pool_name": "mypool",
    "pool_size": 32,  # 修改为最大允许值 32
    "pool_reset_session": True  # 重置会话
}

# 声明全局变量
global db_pool

# 创建数据库连接池
def create_db_pool():
    global db_pool
    try:
        db_pool = mysql.connector.pooling.MySQLConnectionPool(**db_config)
    except Exception as error:
        print('Error creating database pool:', str(error))
        raise

# 初始化连接池
create_db_pool()

# 添加连接池管理
def get_db_connection():
    global db_pool
    max_retries = 3
    retry_count = 0

    while retry_count < max_retries:
        try:
            conn = db_pool.get_connection()
            if conn.is_connected():
                return conn
        except Exception as error:
            print(f'Error getting connection (attempt {retry_count + 1}): {str(error)}')
            retry_count += 1
            if retry_count == max_retries:
                # 最后一次尝试，重新创建连接池
                try:
                    create_db_pool()
                    conn = db_pool.get_connection()
                    if conn.is_connected():
                        return conn
                except Exception as pool_error:
                    print(f'Error recreating pool: {str(pool_error)}')
                    raise
            time.sleep(0.1)  # 短暂延迟后重试

    raise Exception('Failed to get database connection after multiple attempts')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# 视频上传路由
@app.route('/api/upload/video', methods=['POST'])
def upload_video():
    try:
        print("Received video upload request")  # 添加日志
        
        if 'file' not in request.files:
            print("No file part in request")  # 添加日志
            return jsonify({
                'code': 1,
                'message': 'No file part'
            }), 400

        file = request.files['file']
        if file.filename == '':
            print("No selected file")  # 添加日志
            return jsonify({
                'code': 1,
                'message': 'No selected file'
            }), 400

        # 检查文件类型
        if not file.filename.lower().endswith(('.mp4', '.mov', '.avi', '.wmv')):
            print(f"Invalid file type: {file.filename}")  # 添加日志
            return jsonify({
                'code': 1,
                'message': 'Invalid video format'
            }), 400

        # 确保上传目录存在
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4()}_{filename}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)

        print(f"Saving file to: {file_path}")  # 添加日志
        file.save(file_path)
        print("File saved successfully")  # 添加日志

        return jsonify({
            'code': 0,
            'message': 'Upload successful',
            'data': {
                'url': f'/uploads/{unique_filename}'
            }
        })

    except Exception as error:
        print('Error uploading video:', str(error))  # 添加详细错误日志
        return jsonify({
            'code': 1,
            'message': f'Upload failed: {str(error)}'
        }), 500


# 批量图片上传
@app.route('/api/upload/images', methods=['POST'])
def upload_multiple_images():
    try:
        if 'files[]' not in request.files:
            return jsonify({
                'code': 1,
                'message': 'No file part'
            }), 400

        files = request.files.getlist('files[]')
        if not files:
            return jsonify({
                'code': 1,
                'message': 'No selected files'
            }), 400

        uploaded_urls = []
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                unique_filename = f"{uuid.uuid4()}_{filename}"
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                file.save(file_path)
                uploaded_urls.append(f'/uploads/{unique_filename}')

        return jsonify({
            'code': 0,
            'message': 'Upload successful',
            'data': {
                'urls': uploaded_urls
            }
        })

    except Exception as error:
        print('Error uploading images:', str(error))
        return jsonify({
            'code': 1,
            'message': str(error)
        }), 500


# API 路由
@app.route('/api/demands', methods=['GET'])
def list_demands():
    try:
        keyword = request.args.get('keyword', '')
        status = request.args.get('status')
        page = int(request.args.get('page', 1))
        size = int(request.args.get('size', 20))

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # 构建基础查询
        base_query = '''
            SELECT 
                d.demand_id,
                d.marketing_number,
                d.dingtalk_number,
                d.asin,
                d.assessment_quantity,
                d.text_review_quantity,
                d.image_review_quantity,
                d.video_review_quantity,
                d.product_price,
                d.search_keyword,
                d.hyperlink,
                d.other_notes,
                d.status_id,
                ds.status_name,
                d.ordered_quantity,
                d.unordered_quantity,
                d.reviewed_quantity,
                d.unreviewed_quantity,
                d.registration_date,
                d.first_order_date
            FROM demands d
            LEFT JOIN demand_status ds ON d.status_id = ds.status_id
        '''

        # 构建 WHERE 条件
        conditions = []
        params = []

        if keyword:
            conditions.append('''
                (d.marketing_number LIKE %s 
                OR d.dingtalk_number LIKE %s 
                OR d.asin LIKE %s)
            ''')
            search_param = f'%{keyword}%'
            params.extend([search_param, search_param, search_param])

        if status:
            conditions.append('d.status_id = %s')
            params.append(int(status))

        # 添加 WHERE 子句
        if conditions:
            base_query += ' WHERE ' + ' AND '.join(conditions)

        # 获取总数
        count_query = f'SELECT COUNT(*) as total FROM ({base_query}) as t'
        cursor.execute(count_query, params)
        total = cursor.fetchone()['total']

        # 添加排序和分页
        query = base_query + ' ORDER BY d.demand_id DESC LIMIT %s OFFSET %s'
        params.extend([size, (page - 1) * size])

        # 执行查询
        cursor.execute(query, params)
        rows = cursor.fetchall()

        # 处理数据
        for row in rows:
            # 确保数值字段为数字类型
            row['assessment_quantity'] = int(row['assessment_quantity'] or 0)
            row['text_review_quantity'] = int(row['text_review_quantity'] or 0)
            row['image_review_quantity'] = int(row['image_review_quantity'] or 0)
            row['video_review_quantity'] = int(row['video_review_quantity'] or 0)
            row['product_price'] = float(row['product_price'] or 0)
            row['ordered_quantity'] = int(row['ordered_quantity'] or 0)
            row['unordered_quantity'] = int(row['unordered_quantity'] or 0)
            row['reviewed_quantity'] = int(row['reviewed_quantity'] or 0)
            row['unreviewed_quantity'] = int(row['unreviewed_quantity'] or 0)

            # 添加默认值
            row['status_name'] = row.get('status_name', '未知')

        cursor.close()
        conn.close()

        return jsonify({
            'code': 0,
            'message': 'success',
            'data': {
                'list': rows,
                'total': total
            }
        })

    except Exception as error:
        print('Error fetching demands:', str(error))
        return jsonify({
            'code': 1,
            'message': str(error)
        }), 500

# 辅助函数
def get_intermediary_status_text(status):
    status_map = {
        1: '未开始',
        2: '进行中',
        3: '已取消',
        4: '已完成'
    }
    return status_map.get(status, '未知')

def get_payment_status_text(status):
    status_map = {
        1: '未支付',
        2: '部分支付',
        3: '已支付'
    }
    return status_map.get(status, '未知')

@app.route('/api/demands', methods=['POST'])
def create_demand():
    try:
        data = request.json
        required_fields = [
            'marketing_number', 'dingtalk_number', 'asin', 'assessment_quantity',
            'status_id', 'model_id', 'type_id', 'platform_id', 'country_id',
            'brand_id', 'store_id', 'account_id', 'method_id',
            'ad_entry_option_id', 'variant_option_id'
        ]

        # 验证必填字段
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400

        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = """
            INSERT INTO demands (
                marketing_number, dingtalk_number, asin, assessment_quantity,
                text_review_quantity, image_review_quantity, video_review_quantity,
                free_review_quantity, like_only_quantity, fb_order_quantity,
                ordered_quantity, unordered_quantity, reviewed_quantity,
                unreviewed_quantity, registration_date, first_order_date,
                product_price, search_keyword, hyperlink,
                product_image_url, received_product_image_url, order_style,
                attribute_value_1, attribute_value_2, other_notes, status_id,
                model_id, type_id, platform_id, country_id, brand_id, store_id,
                account_id, method_id, ad_entry_option_id, variant_option_id
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s
            )
        """
        
        values = (
            data.get('marketing_number'),
            data.get('dingtalk_number'),
            data.get('asin'),
            data.get('assessment_quantity'),
            data.get('text_review_quantity', 0),
            data.get('image_review_quantity', 0),
            data.get('video_review_quantity', 0),
            data.get('free_review_quantity', 0),
            data.get('like_only_quantity', 0),
            data.get('fb_order_quantity', 0),
            data.get('ordered_quantity', 0),
            data.get('unordered_quantity', 0),
            data.get('reviewed_quantity', 0),
            data.get('unreviewed_quantity', 0),
            data.get('registration_date'),
            data.get('first_order_date'),
            data.get('product_price'),
            data.get('search_keyword'),
            data.get('hyperlink'),
            data.get('product_image_url'),
            data.get('received_product_image_url'),
            data.get('order_style'),
            data.get('attribute_value_1'),
            data.get('attribute_value_2'),
            data.get('other_notes'),
            data.get('status_id'),
            data.get('model_id'),
            data.get('type_id'),
            data.get('platform_id'),
            data.get('country_id'),
            data.get('brand_id'),
            data.get('store_id'),
            data.get('account_id'),
            data.get('method_id'),
            data.get('ad_entry_option_id'),
            data.get('variant_option_id')
        )
        
        cursor.execute(query, values)
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({'message': 'Demand created successfully'}), 201
    except Exception as error:
        print('Error creating demand:', str(error))
        return jsonify({'error': str(error)}), 500

@app.route('/basic-api/upload/images', methods=['POST', 'OPTIONS'])
def upload_images():
    # 处理 OPTIONS 请求
    if request.method == 'OPTIONS':
        response = app.make_default_options_response()
        return response

    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
            
        files = request.files.getlist('file')
        if not files:
            return jsonify({'error': 'No files selected'}), 400
            
        if len(files) > MAX_IMAGES_PER_REQUEST:
            return jsonify({'error': f'Maximum {MAX_IMAGES_PER_REQUEST} images allowed'}), 400
            
        uploaded_urls = []
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                unique_filename = f"{uuid.uuid4()}_{filename}"
                
                if not os.path.exists(app.config['UPLOAD_FOLDER']):
                    os.makedirs(app.config['UPLOAD_FOLDER'])
                    
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                file.save(file_path)
                
                uploaded_urls.append(f'/uploads/{unique_filename}')
            else:
                return jsonify({'error': 'Invalid file type'}), 400
        
        return jsonify({
            'code': 0,
            'message': 'Upload successful',
            'result': {
                'url': uploaded_urls[0] if len(uploaded_urls) == 1 else uploaded_urls
            }
        })
        
    except Exception as error:
        return jsonify({
            'code': 1,
            'message': str(error)
        }), 500

# 修改图片预览路由
@app.route('/basic-api/uploads/<path:filename>')
def serve_upload(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# 静态文件服务
@app.route('/uploads/<filename>')
def serve_uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path.startswith('api'):
        return jsonify({'error': 'API not found'}), 404
    
    if path == '':
        return send_file('public/index.html')
        
    file_path = os.path.join('public', path)
    if os.path.exists(file_path):
        return send_file(file_path)
    else:
        return send_file('public/index.html')

# 数据库检查函数
def check_database():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 检查demands表是否存在
        cursor.execute("""
            SELECT COUNT(*)
            FROM information_schema.tables
            WHERE table_schema = 'assessment_business'
            AND table_name = 'demands'
        """)
        if cursor.fetchone()[0] == 0:
            print("Warning: 'demands' table does not exist")
            
        # 检查demand_status表是否存在
        cursor.execute("""
            SELECT COUNT(*)
            FROM information_schema.tables
            WHERE table_schema = 'assessment_business'
            AND table_name = 'demand_status'
        """)
        if cursor.fetchone()[0] == 0:
            print("Warning: 'demand_status' table does not exist")
            
        cursor.close()
        conn.close()
    except Exception as error:
        print("Database check failed:", str(error))
        raise error

# API 路由
@app.route('/api/demand_status', methods=['GET'])
def get_demand_status():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM demand_status')
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(rows)
    except Exception as error:
        print('Error fetching demand status:', str(error))
        return jsonify({'error': str(error)}), 500

@app.route('/api/product_models', methods=['GET'])
def get_product_models():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM product_models')
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(rows)
    except Exception as error:
        return jsonify({'error': str(error)}), 500

@app.route('/api/demands/<dingtalk_number>', methods=['GET'])
def get_demand(dingtalk_number):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM demands WHERE dingtalk_number = %s', (dingtalk_number,))
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        if not row:
            return jsonify({'error': 'Demand not found'}), 404
        return jsonify(row)
    except Exception as error:
        return jsonify({'error': str(error)}), 500

@app.route('/api/demands/<dingtalk_number>', methods=['PUT'])
def update_demand(dingtalk_number):
    try:
        data = request.json
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = """
            UPDATE demands SET 
                marketing_number = %s, asin = %s, assessment_quantity = %s,
                text_review_quantity = %s, image_review_quantity = %s,
                video_review_quantity = %s, status_id = %s
            WHERE dingtalk_number = %s
        """
        
        values = (
            data.get('marketing_number'),
            data.get('asin'),
            data.get('assessment_quantity'),
            data.get('text_review_quantity'),
            data.get('image_review_quantity'),
            data.get('video_review_quantity'),
            data.get('status_id'),
            dingtalk_number
        )
        
        cursor.execute(query, values)
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'message': 'Demand updated successfully'})
    except Exception as error:
        return jsonify({'error': str(error)}), 500

@app.route('/api/demands/<dingtalk_number>', methods=['DELETE'])
def delete_demand(dingtalk_number):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM demands WHERE dingtalk_number = %s', (dingtalk_number,))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'message': 'Demand deleted successfully'})
    except Exception as error:
        return jsonify({'error': str(error)}), 500

# 获取所有业务类型
@app.route('/api/business_types', methods=['GET'])
def get_business_types():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM business_types')
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(rows)
    except Exception as error:
        return jsonify({'error': str(error)}), 500

# 获取所有平台
@app.route('/api/platforms', methods=['GET'])
def get_platforms():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM platforms')
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(rows)
    except Exception as error:
        return jsonify({'error': str(error)}), 500

# 获取所有国家
@app.route('/api/countries', methods=['GET'])
def get_countries():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM countries')
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(rows)
    except Exception as error:
        return jsonify({'error': str(error)}), 500

# 获取所有品牌
@app.route('/api/brands', methods=['GET'])
def get_brands():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM brands')
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(rows)
    except Exception as error:
        return jsonify({'error': str(error)}), 500

# 获取所有店铺
@app.route('/api/stores', methods=['GET'])
def get_stores():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT store_id, store_name FROM stores')
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(rows)
    except Exception as error:
        print('Error fetching stores:', str(error))
        return jsonify({'error': str(error)}), 500

# 获取所有账号
@app.route('/api/accounts', methods=['GET'])
def get_accounts():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM accounts')
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(rows)
    except Exception as error:
        return jsonify({'error': str(error)}), 500

# 获取所有搜索方式
@app.route('/api/search_methods', methods=['GET'])
def get_search_methods():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM search_methods')
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(rows)
    except Exception as error:
        return jsonify({'error': str(error)}), 500

# 获取所有广告入口选项
@app.route('/api/ad_entry_options', methods=['GET'])
def get_ad_entry_options():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM ad_entry_options')
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(rows)
    except Exception as error:
        return jsonify({'error': str(error)}), 500

# 获取所有变体选项
@app.route('/api/variant_options', methods=['GET'])
def get_variant_options():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM variant_options')
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(rows)
    except Exception as error:
        return jsonify({'error': str(error)}), 500

# 添加导入历史记录的API
@app.route('/api/demands/import-history', methods=['GET'])
def get_import_history():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM import_history ORDER BY import_time DESC')
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(rows)
    except Exception as error:
        return jsonify({'error': str(error)}), 500

# 添加数据验证函数
def validate_foreign_keys(cursor, row):
    errors = []
    
    # 验证状态ID
    if not pd.isna(row.get('状态ID')):
        cursor.execute('SELECT 1 FROM demand_status WHERE status_id = %s', (int(row['状态ID']),))
        if not cursor.fetchone():
            errors.append(f'状态ID {int(row["状态ID"])} 不存在')
    
    # 验证产品型号ID
    if not pd.isna(row.get('产品型号ID')):
        cursor.execute('SELECT 1 FROM product_models WHERE model_id = %s', (int(row['产品型号ID']),))
        if not cursor.fetchone():
            errors.append(f'产品型号ID {int(row["产品型号ID"])} 不存在')
    
    # 验证其他外键...
    foreign_key_mappings = [
        ('运营类型ID', 'business_types', 'type_id'),
        ('平台ID', 'platforms', 'platform_id'),
        ('国家ID', 'countries', 'country_id'),
        ('品牌ID', 'brands', 'brand_id'),
        ('店铺ID', 'stores', 'store_id'),
        ('账号ID', 'accounts', 'account_id'),
        ('搜索方式ID', 'search_methods', 'method_id'),
        ('广告入口ID', 'ad_entry_options', 'option_id'),
        ('变体选项ID', 'variant_options', 'option_id'),
    ]
    
    for excel_field, table, db_field in foreign_key_mappings:
        if not pd.isna(row.get(excel_field)):
            cursor.execute(f'SELECT 1 FROM {table} WHERE {db_field} = %s', (int(row[excel_field]),))
            if not cursor.fetchone():
                errors.append(f'{excel_field} {int(row[excel_field])} 不存在')
    
    return errors

# 修改预览API，添加外键验证
@app.route('/api/demands/preview', methods=['POST'])
def preview_import():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
            
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
            
        if not file.filename.endswith('.xlsx'):
            return jsonify({'error': 'Only .xlsx files are allowed'}), 400
            
        # 读取Excel文件
        df = pd.read_excel(file)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 验证数据
        preview_data = []
        errors = []
        
        for index, row in df.iterrows():
            row_data = {
                'row_number': index + 2,
                'marketing_number': str(row.get('营销编号', '')),
                'dingtalk_number': str(row.get('钉钉号', '')),
                'asin': str(row.get('ASIN', '')),
                'assessment_quantity': int(row['评估数量']) if not pd.isna(row.get('评估数量')) else None,
                'status_id': int(row['状态ID']) if not pd.isna(row.get('状态ID')) else None,
                'validation_errors': []
            }
            
            # 验证必填字段
            required_fields = ['营销编号', '钉钉号', 'ASIN', '评估数量', '状态ID']
            for field in required_fields:
                if pd.isna(row.get(field)):
                    row_data['validation_errors'].append(f'{field}不能为空')
            
            # 验证数据类型
            try:
                if not pd.isna(row.get('评估数量')):
                    int(row['评估数量'])
                    if int(row['评估数量']) <= 0:
                        row_data['validation_errors'].append('评估数量必须大于0')
            except ValueError:
                row_data['validation_errors'].append('评估数量必须是数字')
            
            # 验证价格
            if not pd.isna(row.get('产品价格')):
                try:
                    price = float(row['产品价格'])
                    if price < 0:
                        row_data['validation_errors'].append('产品价格不能为负数')
                except ValueError:
                    row_data['validation_errors'].append('产品价格必须是数字')
            
            # 验证外键
            if not row_data['validation_errors']:  # 只有在基本验证通过后才验证外键
                fk_errors = validate_foreign_keys(cursor, row)
                row_data['validation_errors'].extend(fk_errors)
            
            preview_data.append(row_data)
            if row_data['validation_errors']:
                errors.append(f"第 {row_data['row_number']} 行: {', '.join(row_data['validation_errors'])}")
        
        cursor.close()
        conn.close()
        
        # 获取各种ID的映射关系，用于前端显示
        mappings = {
            'status': get_demand_status_map(),
            'model': get_product_model_map(),
            'type': get_business_type_map(),
            'platform': get_platform_map(),
            'country': get_country_map(),
            'brand': get_brand_map(),
            'store': get_store_map(),
            'account': get_account_map(),
        }
        
        return jsonify({
            'preview_data': preview_data[:10],  # 只返回前10行预览
            'total_rows': len(df),
            'error_count': len(errors),
            'errors': errors,
            'mappings': mappings
        })
        
    except Exception as error:
        return jsonify({
            'error': str(error),
            'message': 'Preview failed'
        }), 500

# 添加获取映射关系的辅助函数
def get_demand_status_map():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT status_id, status_name FROM demand_status')
    result = {str(row['status_id']): row['status_name'] for row in cursor.fetchall()}
    cursor.close()
    conn.close()
    return result

def get_product_model_map():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT model_id, model_name FROM product_models')
    result = {str(row['model_id']): row['model_name'] for row in cursor.fetchall()}
    cursor.close()
    conn.close()
    return result

# ... 其他映射函数类似

@app.route('/api/demands/template', methods=['GET'])
def get_demand_template():
    try:
        # 创建一个新的Excel工作簿
        output = BytesIO()
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet()
        
        # 添加表头
        headers = [
            '营销编号', '钉钉号', 'ASIN', '评估数量',
            '文字评论数', '图片评论数', '视频评论数',
            '产品价格', '搜索关键词', '链接', '备注'
        ]
        
        # 设置表头格式
        header_format = workbook.add_format({
            'bold': True,
            'align': 'center',
            'valign': 'vcenter',
            'fg_color': '#D9D9D9',
            'border': 1
        })
        
        # 写入表头
        for col, header in enumerate(headers):
            worksheet.write(0, col, header, header_format)
            worksheet.set_column(col, col, 15)  # 设置列宽
        
        # 添加示例数据
        example_data = [
            'MK20240101001', 'DT20240101001', 'B0XXXXX',
            10, 5, 3, 2, 99.99, '关键词1 关键词2',
            'https://example.com', '备注信息'
        ]
        
        # 设置示例数据格式
        data_format = workbook.add_format({
            'align': 'center',
            'valign': 'vcenter',
            'border': 1
        })
        
        # 写入示例数据
        for col, value in enumerate(example_data):
            worksheet.write(1, col, value, data_format)
        
        # 关闭工作簿
        workbook.close()
        
        # 设置响应头
        output.seek(0)
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name='需求导入模板.xlsx'
        )
        
    except Exception as error:
        print('Error generating template:', str(error))
        return jsonify({
            'code': 1,
            'message': str(error)
        }), 500

# 添加登录路由
@app.route('/api/login', methods=['POST'])
def login():
  data = request.json
  if data.get('username') == 'vben' and data.get('password') == '123456':
    # 创建 JWT token
    access_token = create_access_token(identity={
      'id': '1',
      'username': 'vben',
      'realName': 'Vben Admin',
      'roles': ['super']
    })

    return jsonify({
      'code': 0,
      'result': {
        'token': access_token,  # 返回 JWT token
        'roles': ['super'],
        'userId': '1',
        'username': 'vben',
        'realName': 'Vben Admin'
      }
    })
  return jsonify({'code': 1, 'message': '用户名或密码错误'}), 401


@app.route('/api/getUserInfo', methods=['GET'])
@jwt_required()  # 需要 JWT 认证
def get_user_info():
  # 从 JWT 中获取用户信息
  current_user = get_jwt_identity()
  return jsonify({
    'code': 0,
    'result': {
      'roles': ['super'],
      'userId': current_user.get('id'),
      'username': current_user.get('username'),
      'realName': current_user.get('realName'),
      'desc': 'manager'
    }
  })

# 导出测评需求
@app.route('/api/demands/export', methods=['GET'])
def export_demands():
    try:
        # 获取查询参数
        keyword = request.args.get('keyword', '')
        status = request.args.get('status')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 构建查询条件
        conditions = []
        params = []
        
        if keyword:
            conditions.append('''
                (d.marketing_number LIKE %s 
                OR d.dingtalk_number LIKE %s 
                OR d.asin LIKE %s)
            ''')
            search_param = f'%{keyword}%'
            params.extend([search_param, search_param, search_param])
            
        if status:
            conditions.append('d.status_id = %s')
            params.append(int(status))
            
        if start_date:
            conditions.append('d.registration_date >= %s')
            params.append(start_date)
            
        if end_date:
            conditions.append('d.registration_date <= %s')
            params.append(end_date)
            
        # 构建基础查询
        query = '''
            SELECT 
                d.marketing_number as '营销编号',
                d.dingtalk_number as '钉钉号',
                d.asin as 'ASIN',
                d.assessment_quantity as '评估数量',
                d.text_review_quantity as '文字评论数',
                d.image_review_quantity as '图片评论数',
                d.video_review_quantity as '视频评论数',
                d.product_price as '产品价格',
                d.ordered_quantity as '已下单数',
                d.unordered_quantity as '未下单数',
                d.reviewed_quantity as '已评价数',
                d.unreviewed_quantity as '未评价数',
                ds.status_name as '状态',
                d.registration_date as '登记日期',
                d.first_order_date as '首单日期',
                d.search_keyword as '搜索关键词',
                d.hyperlink as '链接',
                d.other_notes as '备注'
            FROM demands d
            LEFT JOIN demand_status ds ON d.status_id = ds.status_id
        '''
        
        # 添加查询条件
        if conditions:
            query += ' WHERE ' + ' AND '.join(conditions)
            
        # 添加排序
        query += ' ORDER BY d.demand_id DESC'
        
        # 执行查询
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        # 创建Excel文件
        output = BytesIO()
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet()
        
        # 设置表头格式
        header_format = workbook.add_format({
            'bold': True,
            'align': 'center',
            'valign': 'vcenter',
            'fg_color': '#D9D9D9',
            'border': 1
        })
        
        # 设置数据格式
        data_format = workbook.add_format({
            'align': 'center',
            'valign': 'vcenter',
            'border': 1
        })
        
        # 写入表头
        for col, field in enumerate(cursor.column_names):
            worksheet.write(0, col, field, header_format)
            worksheet.set_column(col, col, 15)  # 设置列宽
            
        # 写入数据
        for row_idx, row in enumerate(rows, 1):
            for col_idx, value in enumerate(row):
                worksheet.write(row_idx, col_idx, value, data_format)
                
        # 关闭工作簿
        workbook.close()
        
        # 设置响应头
        output.seek(0)
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=f'需求列表_{datetime.now().strftime("%Y%m%d")}.xlsx'
        )
        
    except Exception as error:
        print('Error exporting demands:', str(error))
        return jsonify({
            'code': 1,
            'message': str(error)
        }), 500

# 导出测评明细
@app.route('/api/demands/export-details', methods=['GET'])
def export_demand_details():
    try:
        conn = get_db_connection()
        query = '''
            SELECT 
                d.*,
                ds.status_name,
                i.name as intermediary_name,
                pm.model_name,
                bt.type_name,
                p.platform_name,
                c.country_name,
                b.brand_name,
                s.store_name,
                a.account_name,
                sm.method_name,
                aeo.option_name as ad_entry_option_name,
                vo.option_name as variant_option_name
            FROM demands d
            LEFT JOIN demand_status ds ON d.status_id = ds.status_id
            LEFT JOIN intermediaries i ON d.intermediary_id = i.id
            LEFT JOIN product_models pm ON d.model_id = pm.model_id
            LEFT JOIN business_types bt ON d.type_id = bt.type_id
            LEFT JOIN platforms p ON d.platform_id = p.platform_id
            LEFT JOIN countries c ON d.country_id = c.country_id
            LEFT JOIN brands b ON d.brand_id = b.brand_id
            LEFT JOIN stores s ON d.store_id = s.store_id
            LEFT JOIN accounts a ON d.account_id = a.account_id
            LEFT JOIN search_methods sm ON d.method_id = sm.method_id
            LEFT JOIN ad_entry_options aeo ON d.ad_entry_option_id = aeo.option_id
            LEFT JOIN variant_options vo ON d.variant_option_id = vo.option_id
        '''
        df = pd.read_sql(query, conn)
        
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='测评明细', index=False)
            
            workbook = writer.book
            worksheet = writer.sheets['测评明细']
            
            for i, col in enumerate(df.columns):
                max_length = max(df[col].astype(str).apply(len).max(), len(col)) + 2
                worksheet.set_column(i, i, max_length)
        
        output.seek(0)
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=f'测评明细_{datetime.now().strftime("%Y%m%d")}.xlsx'
        )
    except Exception as error:
        return jsonify({'error': str(error)}), 500

# 批量上传图片
@app.route('/api/demands/import-images', methods=['POST'])
def import_demand_images():
    try:
        # 验证参数
        demand_id = request.form.get('demand_id')
        detail_id = request.form.get('detail_id')
        image_type = request.form.get('image_type')
        
        print(f"Received request - demand_id: {demand_id}, detail_id: {detail_id}, image_type: {image_type}")
        print(f"Files in request: {request.files.keys()}")
        
        if not demand_id:
            return jsonify({
                'code': 1,
                'message': 'Missing demand_id'
            }), 400
            
        if not image_type or image_type not in ['order', 'review', 'payment']:
            return jsonify({
                'code': 1,
                'message': 'Invalid image_type'
            }), 400
            
        if 'files[]' not in request.files:
            return jsonify({
                'code': 1,
                'message': 'No files uploaded'
            }), 400
            
        files = request.files.getlist('files[]')
        if not files:
            return jsonify({
                'code': 1,
                'message': 'No files selected'
            }), 400
            
        # 确保上传目录存在
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        
        uploaded_files = []
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 验证需求ID是否存在
        cursor.execute('SELECT demand_id FROM demands WHERE demand_id = %s', (demand_id,))
        if not cursor.fetchone():
            return jsonify({
                'code': 1,
                'message': 'Invalid demand_id'
            }), 400
            
        # 如果提供了明细ID，验证它是否存在且属于该需求
        if detail_id:
            cursor.execute(
                'SELECT detail_id FROM demand_details WHERE detail_id = %s AND demand_id = %s',
                (detail_id, demand_id)
            )
            if not cursor.fetchone():
                return jsonify({
                    'code': 1,
                    'message': 'Invalid detail_id'
                }), 400
        
        for file in files:
            if file and allowed_file(file.filename):
                try:
                    filename = secure_filename(file.filename)
                    unique_filename = f"{uuid.uuid4()}_{filename}"
                    file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                    
                    print(f"Saving file to: {file_path}")
                    
                    # 保存并处理图片
                    file.save(file_path)
                    with Image.open(file_path) as img:
                        if max(img.size) > 1920:
                            img.thumbnail((1920, 1920))
                        img.save(file_path, optimize=True, quality=85)
                    
                    image_url = f'/uploads/{unique_filename}'
                    
                    # 保存图片记录
                    cursor.execute('''
                        INSERT INTO demand_images (
                            demand_id, detail_id, image_type, image_url, original_name
                        ) VALUES (%s, %s, %s, %s, %s)
                    ''', (demand_id, detail_id, image_type, image_url, filename))
                    
                    # 如果是明细相关的图片，更新明细记录
                    if detail_id:
                        field_name = f'{image_type}_screenshot'
                        cursor.execute(
                            f'UPDATE demand_details SET {field_name} = %s WHERE detail_id = %s',
                            (image_url, detail_id)
                        )
                    
                    uploaded_files.append({
                        'original_name': filename,
                        'saved_name': unique_filename,
                        'url': image_url,
                        'type': image_type
                    })
                except Exception as e:
                    print(f"Error processing file {filename}: {str(e)}")
                    continue
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            'code': 0,
            'message': 'Upload successful',
            'data': uploaded_files
        })
        
    except Exception as error:
        print('Error importing images:', str(error))
        return jsonify({
            'code': 1,
            'message': str(error)
        }), 500

# 添加获取所有选项的 API
@app.route('/api/options', methods=['GET'])
def get_all_options():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # 获取所有选项数据
        options = {}
        
        # 获取状态选项
        cursor.execute('SELECT status_id, status_name FROM demand_status')
        options['status'] = cursor.fetchall()
        
        # 获取产品型号选项
        cursor.execute('SELECT model_id, model_name FROM product_models')
        options['models'] = cursor.fetchall()
        
        # 获取业务类型选项
        cursor.execute('SELECT type_id, type_name FROM business_types')
        options['types'] = cursor.fetchall()
        
        # 获取平台选项
        cursor.execute('SELECT platform_id, platform_name FROM platforms')
        options['platforms'] = cursor.fetchall()
        
        # 获取国家选项
        cursor.execute('SELECT country_id, country_name FROM countries')
        options['countries'] = cursor.fetchall()
        
        # 获取品牌选项
        cursor.execute('SELECT brand_id, brand_name FROM brands')
        options['brands'] = cursor.fetchall()
        
        # 获取店铺选项
        cursor.execute('SELECT store_id, store_name FROM stores')
        options['stores'] = cursor.fetchall()
        
        # 获取账号选项
        cursor.execute('SELECT account_id, account_name FROM accounts')
        options['accounts'] = cursor.fetchall()
        
        # 获取搜索方式选项
        cursor.execute('SELECT method_id, method_name FROM search_methods')
        options['methods'] = cursor.fetchall()
        
        # 获取广告入口选项
        cursor.execute('SELECT option_id, option_name FROM ad_entry_options')
        options['adEntryOptions'] = cursor.fetchall()
        
        # 获取变体选项
        cursor.execute('SELECT option_id, option_name FROM variant_options')
        options['variantOptions'] = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return jsonify(options)
    except Exception as error:
        print('Error fetching options:', str(error))
        return jsonify({'error': str(error)}), 500

# 获取中介列表
@app.route('/api/intermediaries', methods=['GET'])
def get_intermediaries():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT mediator_id as id, mediator_name as name FROM mediators')
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(rows)
    except Exception as error:
        print('Error fetching intermediaries:', str(error))
        return jsonify({'error': str(error)}), 500

# 获取中介状态
@app.route('/api/intermediary_status', methods=['GET'])
def get_intermediary_status():
    try:
        # 返回固定的中介状态选项
        status_options = [
            {'status_id': 1, 'status_name': '未开始'},
            {'status_id': 2, 'status_name': '进行中'},
            {'status_id': 3, 'status_name': '已取消'},
            {'status_id': 4, 'status_name': '已完成'}
        ]
        return jsonify(status_options)
    except Exception as error:
        print('Error fetching intermediary status:', str(error))
        return jsonify({'error': str(error)}), 500

# 获取支付状态
@app.route('/api/payment_status', methods=['GET'])
def get_payment_status():
    try:
        # 返回固定的支付状态选项
        status_options = [
            {'status_id': 1, 'status_name': '未支付'},
            {'status_id': 2, 'status_name': '部分支付'},
            {'status_id': 3, 'status_name': '已支付'}
        ]
        return jsonify(status_options)
    except Exception as error:
        print('Error fetching payment status:', str(error))
        return jsonify({'error': str(error)}), 500

# 创建测评明细时关联中介
@app.route('/api/demands/<int:demand_id>/details', methods=['POST'])
def create_demand_detail(demand_id):
    try:
        data = request.json
        agent_id = data.pop('agent_id', None)  # 从请求数据中提取中介ID
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # 处理图片列表
        if isinstance(data.get('review_images'), list):
            data['review_images'] = ','.join([str(img) for img in data['review_images'] if img])

        # 处理日期时间格式
        if data.get('order_time'):
            try:
                order_time = datetime.strptime(data['order_time'], '%a, %d %b %Y %H:%M:%S GMT')
                data['order_time'] = order_time.strftime('%Y-%m-%d %H:%M:%S')
            except Exception as e:
                print(f"Error parsing order_time: {e}")
                
        if data.get('review_time'):
            try:
                review_time = datetime.strptime(data['review_time'], '%a, %d %b %Y %H:%M:%S GMT')
                data['review_time'] = review_time.strftime('%Y-%m-%d %H:%M:%S')
            except Exception as e:
                print(f"Error parsing review_time: {e}")
        
        # 检查需求是否存在
        cursor.execute("SELECT demand_id FROM demands WHERE demand_id = %s", (demand_id,))
        if not cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({
                'code': 1,
                'message': '需求不存在'
            }), 404
            
        # 准备插入字段
        fields = [field for field in data.keys()]
        placeholders = ', '.join(['%s'] * len(fields))
        values = [data[field] for field in fields]
        
        # 添加需求ID
        fields.append('demand_id')
        values.append(demand_id)
        
        # 准备order_id字段
        order_id = None
        
        # 如果提供了中介ID，查找或创建订单
        if agent_id:
            # 查找该需求下该中介的订单
            cursor.execute("""
                SELECT order_id FROM orders 
                WHERE demand_id = %s AND agent_id = %s
            """, (demand_id, agent_id))
            
            order_result = cursor.fetchone()
            
            if order_result:
                # 使用现有订单
                order_id = order_result['order_id']
            else:
                # 创建新订单
                order_number = f"ORD-{demand_id}-{agent_id}-{int(time.time())}"
                cursor.execute("""
                    INSERT INTO orders (demand_id, agent_id, order_number, target_count, actual_count, status)
                    VALUES (%s, %s, %s, 1, 0, 1)
                """, (demand_id, agent_id, order_number))
                order_id = cursor.lastrowid
        
        # 如果找到或创建了订单，添加到字段中
        if order_id:
            fields.append('order_id')
            values.append(order_id)
        
        # 构建INSERT语句
        insert_query = f"""
            INSERT INTO demand_details ({', '.join(fields)})
            VALUES ({', '.join(['%s'] * len(values))})
        """
        
        cursor.execute(insert_query, values)
        detail_id = cursor.lastrowid
        
        # 如果关联了订单，增加实际完成数量
        if order_id:
            cursor.execute("""
                UPDATE orders 
                SET actual_count = actual_count + 1 
                WHERE order_id = %s
            """, (order_id,))
        
        # 获取创建的详情
        cursor.execute('''
            SELECT dd.*, a.agent_id, a.agent_name
            FROM demand_details dd
            LEFT JOIN orders o ON dd.order_id = o.order_id
            LEFT JOIN agents a ON o.agent_id = a.agent_id
            WHERE dd.detail_id = %s
        ''', (detail_id,))
        
        result = cursor.fetchone()
        
        # 处理返回数据中的图片列表
        if result and result.get('review_images'):
            result['review_images'] = result['review_images'].split(',')
        else:
            result['review_images'] = []
            
        # 处理数值字段
        if result and result.get('order_amount'):
            result['order_amount'] = float(result['order_amount'])
        
        conn.commit()
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'code': 0,
            'message': '明细创建成功',
            'data': result
        })
    except Exception as e:
        print('Error creating demand detail:', str(e))
        return jsonify({
            'code': 1,
            'message': str(e)
        }), 500

# 获取需求明细列表
@app.route('/api/demands/<int:demand_id>/details', methods=['GET'])
def get_demand_details(demand_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # 检查需求是否存在
        cursor.execute("SELECT demand_id FROM demands WHERE demand_id = %s", (demand_id,))
        if not cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({
                'code': 1,
                'message': '需求不存在'
            }), 404
            
        # 获取需求明细，包含中介信息
        query = """
            SELECT d.*, a.agent_id, a.agent_name, ds.status_name
            FROM demand_details d
            LEFT JOIN orders o ON d.order_id = o.order_id
            LEFT JOIN agents a ON o.agent_id = a.agent_id
            LEFT JOIN demand_status ds ON d.status = ds.status_id
            WHERE d.demand_id = %s
            ORDER BY d.detail_id DESC
        """
        cursor.execute(query, (demand_id,))
        details = cursor.fetchall()
        
        # 处理每个明细的图片和数值
        for detail in details:
            # 处理图片列表
            if detail.get('review_images'):
                detail['review_images'] = detail['review_images'].split(',')
            else:
                detail['review_images'] = []
                
            # 处理数值字段
            if detail.get('order_amount'):
                detail['order_amount'] = float(detail['order_amount'] or 0)
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'code': 0,
            'message': 'success',
            'data': details
        })
    except Exception as e:
        print('Error getting demand details:', str(e))
        return jsonify({
            'code': 1,
            'message': str(e)
        }), 500

# 获取单个测评明细
@app.route('/api/demand-details/<int:detail_id>', methods=['GET'])
def get_demand_detail(detail_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # 查询包含中介信息的明细详情
        cursor.execute('''
            SELECT dd.*, a.agent_id, a.agent_name, ds.status_name
            FROM demand_details dd
            LEFT JOIN orders o ON dd.order_id = o.order_id
            LEFT JOIN agents a ON o.agent_id = a.agent_id
            LEFT JOIN demand_status ds ON dd.status = ds.status_id
            WHERE dd.detail_id = %s
        ''', (detail_id,))
        
        result = cursor.fetchone()
        
        if not result:
            cursor.close()
            conn.close()
            return jsonify({
                'code': 1,
                'message': '明细不存在'
            }), 404
            
        # 处理返回数据中的图片列表
        if result.get('review_images'):
            result['review_images'] = result['review_images'].split(',')
        else:
            result['review_images'] = []
            
        # 处理数值字段
        if result.get('order_amount'):
            result['order_amount'] = float(result['order_amount'])
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'code': 0,
            'message': 'success',
            'data': result
        })
        
    except Exception as error:
        print('Error getting demand detail:', str(error))
        return jsonify({
            'code': 1,
            'message': str(error)
        }), 500

# 更新测评明细
@app.route('/api/demand-details/<int:detail_id>', methods=['PUT', 'POST'])
def update_demand_detail(detail_id):
    try:
        data = request.json
        print("更新明细请求数据:", data)  # 添加调试日志
        
        agent_id = data.pop('agent_id', None)  # 从请求数据中提取中介ID
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # 检查明细是否存在
        cursor.execute('SELECT detail_id, demand_id, order_id FROM demand_details WHERE detail_id = %s', (detail_id,))
        detail = cursor.fetchone()
        if not detail:
            cursor.close()
            conn.close()
            return jsonify({
                'code': 1,
                'message': '明细不存在'
            }), 404
        
        demand_id = detail['demand_id']
        old_order_id = detail['order_id']
        new_order_id = None
        
        # 处理图片列表 (如果存在)
        if 'review_images' in data and isinstance(data.get('review_images'), list):
            data['review_images'] = ','.join([str(img) for img in data['review_images'] if img])
        
        # 处理中介关联
        if agent_id is not None:  # 包括agent_id=null的情况
            if agent_id:  # 如果agent_id有值
                # 查找该需求下该中介的订单
                cursor.execute("""
                    SELECT order_id FROM orders 
                    WHERE demand_id = %s AND agent_id = %s
                """, (demand_id, agent_id))
                
                order_result = cursor.fetchone()
                
                if order_result:
                    # 使用现有订单
                    new_order_id = order_result['order_id']
                else:
                    # 创建新订单
                    order_number = f"ORD-{demand_id}-{agent_id}-{int(time.time())}"
                    cursor.execute("""
                        INSERT INTO orders (demand_id, agent_id, order_number, target_count, actual_count, status)
                        VALUES (%s, %s, %s, 1, 0, 1)
                    """, (demand_id, agent_id, order_number))
                    new_order_id = cursor.lastrowid
            else:
                # agent_id为null时，取消与订单的关联
                new_order_id = None
        
        # 构建更新语句
        update_fields = []
        update_values = {}
        
        # 更新常规字段
        for key in data:
            update_fields.append(f'{key} = %({key})s')
            update_values[key] = data[key]
        
        # 更新order_id
        if agent_id is not None:  # 只有当提供了agent_id参数时才更新order_id
            if new_order_id:
                update_fields.append('order_id = %(order_id)s')
                update_values['order_id'] = new_order_id
            else:
                update_fields.append('order_id = NULL')
                
        update_values['detail_id'] = detail_id
        
        if not update_fields:
            cursor.close()
            conn.close()
            return jsonify({
                'code': 1,
                'message': '没有需要更新的字段'
            }), 400
        
        # 打印SQL和参数以便调试
        update_query = f'''
            UPDATE demand_details 
            SET {', '.join(update_fields)}
            WHERE detail_id = %(detail_id)s
        '''
        print("更新SQL:", update_query)
        print("参数:", update_values)
        
        cursor.execute(update_query, update_values)
        
        # 处理订单统计
        if agent_id is not None:  # 只有提供了agent_id参数时才处理订单统计
            # 减少旧订单的实际完成数量
            if old_order_id:
                cursor.execute("""
                    UPDATE orders 
                    SET actual_count = GREATEST(actual_count - 1, 0)
                    WHERE order_id = %s
                """, (old_order_id,))
            
            # 增加新订单的实际完成数量
            if new_order_id:
                cursor.execute("""
                    UPDATE orders 
                    SET actual_count = actual_count + 1,
                        completion_rate = (actual_count + 1) / target_count * 100
                    WHERE order_id = %s
                """, (new_order_id,))
        
        conn.commit()
        
        # 获取更新后的数据
        cursor.execute('''
            SELECT dd.*, a.agent_id, a.agent_name
            FROM demand_details dd
            LEFT JOIN orders o ON dd.order_id = o.order_id
            LEFT JOIN agents a ON o.agent_id = a.agent_id
            WHERE dd.detail_id = %s
        ''', (detail_id,))
        
        result = cursor.fetchone()
        
        # 处理返回数据中的图片列表
        if result and result.get('review_images'):
            result['review_images'] = result['review_images'].split(',')
        else:
            result['review_images'] = []
            
        # 处理数值字段
        if result and result.get('order_amount'):
            result['order_amount'] = float(result['order_amount'])
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'code': 0,
            'message': '更新成功',
            'data': result
        })
        
    except Exception as error:
        print('Error updating demand detail:', str(error))
        return jsonify({
            'code': 1,
            'message': str(error)
        }), 500

# 删除测评明细
@app.route('/api/demand-details/<int:detail_id>', methods=['DELETE'])
def delete_demand_detail(detail_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM demand_details WHERE detail_id = %s', (detail_id,))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({'message': 'Detail deleted successfully'})
    except Exception as error:
        print('Error deleting demand detail:', str(error))
        return jsonify({'error': str(error)}), 500

# 导入需求
@app.route('/api/demands/import', methods=['POST'])
def import_demands():
    try:
        if 'file' not in request.files:
            return jsonify({
                'code': 1,
                'message': 'No file part'
            }), 400
            
        file = request.files['file']
        if file.filename == '':
            return jsonify({
                'code': 1,
                'message': 'No selected file'
            }), 400
            
        if not file.filename.endswith('.xlsx'):
            return jsonify({
                'code': 1,
                'message': 'Only .xlsx files are allowed'
            }), 400
            
        # 读取Excel文件
        df = pd.read_excel(file)
        
        # 验证必要的列
        required_columns = [
            'marketing_number', 'dingtalk_number', 'asin', 
            'assessment_quantity', 'text_review_quantity', 
            'image_review_quantity', 'video_review_quantity'
        ]
        
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            return jsonify({
                'code': 1,
                'message': f'Missing required columns: {", ".join(missing_columns)}'
            }), 400
            
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 插入数据
        for _, row in df.iterrows():
            insert_query = '''
                INSERT INTO demands (
                    marketing_number, dingtalk_number, asin,
                    assessment_quantity, text_review_quantity,
                    image_review_quantity, video_review_quantity,
                    product_price, search_keyword, hyperlink,
                    other_notes, status_id
                ) VALUES (
                    %(marketing_number)s, %(dingtalk_number)s, %(asin)s,
                    %(assessment_quantity)s, %(text_review_quantity)s,
                    %(image_review_quantity)s, %(video_review_quantity)s,
                    %(product_price)s, %(search_keyword)s, %(hyperlink)s,
                    %(other_notes)s, 1
                )
            '''
            
            cursor.execute(insert_query, {
                'marketing_number': row['marketing_number'],
                'dingtalk_number': row['dingtalk_number'],
                'asin': row['asin'],
                'assessment_quantity': row['assessment_quantity'],
                'text_review_quantity': row['text_review_quantity'],
                'image_review_quantity': row['image_review_quantity'],
                'video_review_quantity': row['video_review_quantity'],
                'product_price': row['product_price'],
                'search_keyword': row['search_keyword'],
                'hyperlink': row['hyperlink'],
                'other_notes': row['other_notes']
            })
            
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            'code': 0,
            'message': 'Import successful'
        })
        
    except Exception as error:
        print('Error importing demands:', str(error))
        return jsonify({
            'code': 1,
            'message': str(error)
        }), 500


# 单个图片上传路由
@app.route('/api/upload/image', methods=['POST'])
def upload_image():
    try:
        if 'file' not in request.files:
            return jsonify({
                'code': 1,
                'message': 'No file part'
            }), 400
            
        file = request.files['file']
        if file.filename == '':
            return jsonify({
                'code': 1,
                'message': 'No selected file'
            }), 400
            
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # 生成唯一文件名
            unique_filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{filename}"
            file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
            file.save(file_path)
            
            return jsonify({
                'code': 0,
                'message': 'success',
                'data': {
                    'url': f'/uploads/{unique_filename}'
                }
            })
            
    except Exception as error:
        print('Error uploading file:', str(error))
        return jsonify({
            'code': 1,
            'message': str(error)
        }), 500

# 添加静态文件路由
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

# 批量修改状态
@app.route('/api/demands/batch/status', methods=['PUT'])
def batch_update_status():
    try:
        data = request.json
        demand_ids = data.get('demand_ids', [])
        status_id = data.get('status_id')
        
        if not demand_ids or not status_id:
            return jsonify({
                'code': 1,
                'message': 'Missing required fields'
            }), 400
            
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE demands 
            SET status_id = %s
            WHERE demand_id IN ({})
        '''.format(','.join(['%s'] * len(demand_ids))), 
        [status_id] + demand_ids)
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            'code': 0,
            'message': 'success'
        })
        
    except Exception as error:
        print('Error updating status:', str(error))
        return jsonify({
            'code': 1,
            'message': str(error)
        }), 500

# 批量删除
@app.route('/api/demands/batch', methods=['DELETE'])
def batch_delete_demands():
    try:
        data = request.json
        demand_ids = data.get('demand_ids', [])
        
        if not demand_ids:
            return jsonify({
                'code': 1,
                'message': 'Missing demand_ids'
            }), 400
            
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            DELETE FROM demands 
            WHERE demand_id IN ({})
        '''.format(','.join(['%s'] * len(demand_ids))), 
        demand_ids)
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            'code': 0,
            'message': 'success'
        })
        
    except Exception as error:
        print('Error deleting demands:', str(error))
        return jsonify({
            'code': 1,
            'message': str(error)
        }), 500

# 将这个路由移到其他 API 路由的位置
@app.route('/api/demands/stats', methods=['GET'])
def get_demand_stats():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # 获取状态分布
        cursor.execute('''
            SELECT 
                COALESCE(ds.status_name, '未知') as name,
                COUNT(*) as value,
                ds.color as itemStyle
            FROM demands d
            LEFT JOIN demand_status ds ON d.status_id = ds.status_id
            GROUP BY d.status_id, ds.status_name, ds.color
            ORDER BY d.status_id
        ''')
        status_stats = cursor.fetchall()
        
        # 处理颜色数据
        for stat in status_stats:
            if 'itemStyle' in stat:
                stat['itemStyle'] = {'color': stat['itemStyle']}
        
        # 获取进度趋势（最近30天）
        cursor.execute('''
            SELECT 
                DATE_FORMAT(COALESCE(d.registration_date, CURDATE()), '%Y-%m-%d') as date,
                COUNT(*) as total,
                SUM(CASE WHEN d.reviewed_quantity >= d.assessment_quantity THEN 1 ELSE 0 END) as completed
            FROM demands d
            WHERE d.registration_date >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
                OR d.registration_date IS NULL
            GROUP BY DATE_FORMAT(COALESCE(d.registration_date, CURDATE()), '%Y-%m-%d')
            ORDER BY date DESC
            LIMIT 30
        ''')
        progress_stats = cursor.fetchall()
        
        # 获取评论分析
        cursor.execute('''
            SELECT 
                'text' as type,
                COUNT(*) as count
            FROM demands
            WHERE text_review_quantity > 0
            UNION ALL
            SELECT 
                'image' as type,
                COUNT(*) as count
            FROM demands
            WHERE image_review_quantity > 0
            UNION ALL
            SELECT 
                'video' as type,
                COUNT(*) as count
            FROM demands
            WHERE video_review_quantity > 0
        ''')
        review_stats = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'code': 0,
            'message': 'success',
            'data': {
                'status': status_stats,
                'progress': progress_stats,
                'reviews': review_stats
            }
        })
        
    except Exception as error:
        print('Error fetching stats:', str(error))
        return jsonify({
            'code': 1,
            'message': str(error)
        }), 500

# 暂停需求
@app.route('/api/demands/<int:demand_id>/pause', methods=['POST'])
def pause_demand(demand_id):
    try:
        data = request.json
        reason = data.get('reason')
        
        if not reason:
            return jsonify({
                'code': 1,
                'message': 'Missing reason'
            }), 400
            
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 检查需求是否存在
        cursor.execute('SELECT status_id FROM demands WHERE demand_id = %s', (demand_id,))
        demand = cursor.fetchone()
        if not demand:
            return jsonify({
                'code': 1,
                'message': '需求不存在'
            }), 404
            
        # 检查当前状态
        current_status = demand[0]
        if current_status == 2:  # 2 是暂停状态
            return jsonify({
                'code': 1,
                'message': '需求已经是暂停状态'
            }), 400
            
        # 更新状态为暂停
        cursor.execute('''
            UPDATE demands 
            SET status_id = 2  -- 2 是暂停状态
            WHERE demand_id = %s
        ''', (demand_id,))
        
        # 记录暂停原因
        cursor.execute('''
            INSERT INTO change_logs (
                demand_id, change_time, change_description, 
                old_status_id, new_status_id
            ) VALUES (
                %s, NOW(), %s, %s, 2
            )
        ''', (demand_id, f'暂停原因: {reason}', current_status))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            'code': 0,
            'message': 'success'
        })
        
    except Exception as error:
        print('Error pausing demand:', str(error))
        return jsonify({
            'code': 1,
            'message': str(error)
        }), 500

# 继续执行需求
@app.route('/api/demands/<int:demand_id>/resume', methods=['POST'])
def resume_demand(demand_id):
    try:
        data = request.json
        reason = data.get('reason')
        
        if not reason:
            return jsonify({
                'code': 1,
                'message': 'Missing reason'
            }), 400
            
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 检查需求是否存在
        cursor.execute('SELECT status_id FROM demands WHERE demand_id = %s', (demand_id,))
        demand = cursor.fetchone()
        if not demand:
            return jsonify({
                'code': 1,
                'message': '需求不存在'
            }), 404
            
        # 检查当前状态
        current_status = demand[0]
        if current_status != 2:  # 2 是暂停状态
            return jsonify({
                'code': 1,
                'message': '需求不是暂停状态'
            }), 400
            
        # 更新状态为进行中
        cursor.execute('''
            UPDATE demands 
            SET status_id = 1  -- 1 是进行中状态
            WHERE demand_id = %s
        ''', (demand_id,))
        
        # 记录继续执行原因
        cursor.execute('''
            INSERT INTO change_logs (
                demand_id, change_time, change_description,
                old_status_id, new_status_id
            ) VALUES (
                %s, NOW(), %s, 2, 1
            )
        ''', (demand_id, f'继续执行原因: {reason}'))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            'code': 0,
            'message': 'success'
        })
        
    except Exception as error:
        print('Error resuming demand:', str(error))
        return jsonify({
            'code': 1,
            'message': str(error)
        }), 500

# 终止需求
@app.route('/api/demands/<int:demand_id>/stop', methods=['POST'])
def stop_demand(demand_id):
    try:
        data = request.json
        reason = data.get('reason')
        
        if not reason:
            return jsonify({
                'code': 1,
                'message': 'Missing reason'
            }), 400
            
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 检查需求是否存在
        cursor.execute('SELECT status_id FROM demands WHERE demand_id = %s', (demand_id,))
        demand = cursor.fetchone()
        if not demand:
            return jsonify({
                'code': 1,
                'message': '需求不存在'
            }), 404
            
        # 检查当前状态
        current_status = demand[0]
        if current_status == 3:  # 3 是终止状态
            return jsonify({
                'code': 1,
                'message': '需求已经是终止状态'
            }), 400
            
        # 更新状态为终止
        cursor.execute('''
            UPDATE demands 
            SET status_id = 3  -- 3 是终止状态
            WHERE demand_id = %s
        ''', (demand_id,))
        
        # 记录终止原因
        cursor.execute('''
            INSERT INTO change_logs (
                demand_id, change_time, change_description,
                old_status_id, new_status_id
            ) VALUES (
                %s, NOW(), %s, %s, 3
            )
        ''', (demand_id, f'终止原因: {reason}', current_status))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            'code': 0,
            'message': 'success'
        })
        
    except Exception as error:
        print('Error stopping demand:', str(error))
        return jsonify({
            'code': 1,
            'message': str(error)
        }), 500

# 获取状态变更历史
@app.route('/api/demands/<int:demand_id>/history', methods=['GET'])
def get_demand_history(demand_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute('''
            SELECT 
                cl.*,
                old_status.status_name as old_status_name,
                new_status.status_name as new_status_name
            FROM change_logs cl
            LEFT JOIN demand_status old_status ON cl.old_status_id = old_status.status_id
            LEFT JOIN demand_status new_status ON cl.new_status_id = new_status.status_id
            WHERE cl.demand_id = %s
            ORDER BY cl.change_time DESC
        ''', (demand_id,))
        
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return jsonify({
            'code': 0,
            'message': 'success',
            'data': rows
        })
        
    except Exception as error:
        print('Error fetching demand history:', str(error))
        return jsonify({
            'code': 1,
            'message': str(error)
        }), 500

# 获取单个需求详情
@app.route('/api/demands/<int:demand_id>', methods=['GET'])
def get_demand_by_id(demand_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute('''
            SELECT 
                d.*,
                ds.status_name,
                ds.color as status_color,
                b.brand_name,
                s.store_name,
                a.account_name,
                m.method_name
            FROM demands d
            LEFT JOIN demand_status ds ON d.status_id = ds.status_id
            LEFT JOIN brands b ON d.brand_id = b.brand_id
            LEFT JOIN stores s ON d.store_id = s.store_id
            LEFT JOIN accounts a ON d.account_id = a.account_id
            LEFT JOIN search_methods m ON d.method_id = m.method_id
            WHERE d.demand_id = %s
        ''', (demand_id,))
        
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not row:
            return jsonify({
                'code': 1,
                'message': '需求不存在'
            }), 404
            
        # 处理数值字段
        row['assessment_quantity'] = int(row['assessment_quantity'] or 0)
        row['text_review_quantity'] = int(row['text_review_quantity'] or 0)
        row['image_review_quantity'] = int(row['image_review_quantity'] or 0)
        row['video_review_quantity'] = int(row['video_review_quantity'] or 0)
        row['product_price'] = float(row['product_price'] or 0)
        row['ordered_quantity'] = int(row['ordered_quantity'] or 0)
        row['unordered_quantity'] = int(row['unordered_quantity'] or 0)
        row['reviewed_quantity'] = int(row['reviewed_quantity'] or 0)
        row['unreviewed_quantity'] = int(row['unreviewed_quantity'] or 0)
        
        return jsonify({
            'code': 0,
            'message': 'success',
            'data': row
        })
        
    except Exception as error:
        print('Error fetching demand:', str(error))
        return jsonify({
            'code': 1,
            'message': str(error)
        }), 500

# 更新需求
@app.route('/api/demands/<int:demand_id>', methods=['PUT'])
def update_demand_by_id(demand_id):  # 修改函数名
    try:
        data = request.json
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 检查需求是否存在
        cursor.execute('SELECT status_id FROM demands WHERE demand_id = %s', (demand_id,))
        if not cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({
                'code': 1,
                'message': '需求不存在'
            }), 404
            
        # 更新需求信息
        cursor.execute('''
            UPDATE demands 
            SET 
                marketing_number = %s,
                dingtalk_number = %s,
                asin = %s,
                assessment_quantity = %s,
                text_review_quantity = %s,
                image_review_quantity = %s,
                video_review_quantity = %s,
                product_price = %s,
                search_keyword = %s,
                hyperlink = %s,
                other_notes = %s,
                brand_id = %s,
                store_id = %s,
                account_id = %s,
                method_id = %s
            WHERE demand_id = %s
        ''', (
            data['marketing_number'],
            data['dingtalk_number'],
            data['asin'],
            data['assessment_quantity'],
            data['text_review_quantity'],
            data['image_review_quantity'],
            data['video_review_quantity'],
            data['product_price'],
            data['search_keyword'],
            data['hyperlink'],
            data['other_notes'],
            data['brand_id'],
            data['store_id'],
            data['account_id'],
            data['method_id'],
            demand_id
        ))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            'code': 0,
            'message': 'success'
        })
        
    except Exception as error:
        print('Error updating demand:', str(error))
        return jsonify({
            'code': 1,
            'message': str(error)
        }), 500


# 返款订单相关API
@app.route('/api/refunds/orders', methods=['GET'])
def get_refund_orders():
    try:
        page = int(request.args.get('page', 1))
        size = int(request.args.get('size', 20))
        keyword = request.args.get('keyword', '')
        status = request.args.get('status')
        
        offset = (page - 1) * size
        
        # 构建查询条件
        where_clause = []
        params = []
        
        if keyword:
            where_clause.append("""
                (ro.marketing_number LIKE %s 
                OR ro.order_number LIKE %s
                OR ro.dingtalk_number LIKE %s)
            """)
            params.extend([f'%{keyword}%'] * 3)
            
        if status:
            where_clause.append('ro.status = %s')
            params.append(status)
            
        where_sql = ' AND '.join(where_clause) if where_clause else '1=1'
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # 查询总数
        count_sql = f"""
            SELECT COUNT(*) as total 
            FROM refund_orders ro
            WHERE {where_sql}
        """
        cursor.execute(count_sql, params)
        total = cursor.fetchone()['total']
        
        # 查询数据
        query = f"""
            SELECT ro.*, d.marketing_number, dd.order_number
            FROM refund_orders ro
            LEFT JOIN demands d ON ro.demand_id = d.demand_id
            LEFT JOIN demand_details dd ON ro.detail_id = dd.detail_id
            WHERE {where_sql}
            ORDER BY ro.created_at DESC
            LIMIT %s OFFSET %s
        """
        cursor.execute(query, params + [size, offset])
        items = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'code': 0,
            'message': 'success',
            'data': {
                'items': items,
                'total': total
            }
        })
        
    except Exception as error:
        print('Error getting refund orders:', str(error))
        return jsonify({
            'code': 1,
            'message': str(error)
        }), 500

@app.route('/api/refunds/orders/search', methods=['GET'])
def search_refund_orders():
    try:
        keyword = request.args.get('keyword', '')
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # 构建查询
        query = """
            SELECT 
                ro.id,
                ro.demand_id,
                ro.detail_id,
                d.marketing_number,
                dd.order_number,
                ro.order_amount,
                ro.currency,
                ro.status
            FROM refund_orders ro
            LEFT JOIN demands d ON ro.demand_id = d.demand_id
            LEFT JOIN demand_details dd ON ro.detail_id = dd.detail_id
            WHERE d.marketing_number LIKE %s 
            OR dd.order_number LIKE %s
            ORDER BY ro.created_at DESC
            LIMIT 20
        """
        
        search_param = f'%{keyword}%'
        cursor.execute(query, (search_param, search_param))
        items = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'code': 0,
            'message': 'success',
            'data': items
        })
        
    except Exception as error:
        print('Error searching refund orders:', str(error))
        return jsonify({
            'code': 1,
            'message': str(error)
        }), 500

@app.route('/api/refunds/orders', methods=['POST'])
def create_refund_order():
    try:
        data = request.json
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # 检查必填字段
        required_fields = ['demand_id', 'detail_id', 'marketing_number', 'order_number', 
                         'order_amount', 'currency', 'business_type']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({
                    'code': 1,
                    'message': f'Missing required field: {field}'
                }), 400

        # 插入订单数据
        insert_sql = """
            INSERT INTO refund_orders (
                demand_id, detail_id, marketing_number, dingtalk_number,
                asin, intermediary, order_number, order_date, order_amount,
                currency, review_type, business_type, brand, payment_method,
                paypal_principal, rmb_commission, intermediary_commission,
                commission_currency, exchange_rate, actual_payment, status
            ) VALUES (
                %(demand_id)s, %(detail_id)s, %(marketing_number)s, %(dingtalk_number)s,
                %(asin)s, %(intermediary)s, %(order_number)s, %(order_date)s, %(order_amount)s,
                %(currency)s, %(review_type)s, %(business_type)s, %(brand)s, %(payment_method)s,
                %(paypal_principal)s, %(rmb_commission)s, %(intermediary_commission)s,
                %(commission_currency)s, %(exchange_rate)s, %(actual_payment)s, 'pending'
            )
        """
        cursor.execute(insert_sql, data)
        order_id = cursor.lastrowid
        
        # 记录日志
        log_sql = """
            INSERT INTO refund_logs (order_id, action, new_status, operator)
            VALUES (%s, 'create', 'pending', %s)
        """
        cursor.execute(log_sql, (order_id, data.get('operator', 'system')))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            'code': 0,
            'message': 'success',
            'data': { 'id': order_id }
        })
        
    except Exception as error:
        print('Error creating refund order:', str(error))
        return jsonify({
            'code': 1,
            'message': str(error)
        }), 500


@app.route('/api/demands/<int:id>/pause', methods=['PUT'])
def pause_demand_api(id):  # 重命名函数
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # 更新需求状态为暂停
        cursor.execute("""
            UPDATE demands 
            SET status_id = 3 
            WHERE demand_id = %s
        """, (id,))

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({
            'code': 0,
            'message': '需求已暂停'
        })
        
    except Exception as error:
        print('Error pausing demand:', str(error))
        return jsonify({
            'code': 1,
            'message': str(error)
        }), 500


@app.route('/api/demands/<int:id>/resume', methods=['PUT'])
def resume_demand_api(id):  # 重命名函数
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # 更新需求状态为正常
        cursor.execute("""
            UPDATE demands 
            SET status_id = 1
            WHERE demand_id = %s
        """, (id,))

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({
            'code': 0,
            'message': '需求已恢复'
        })
        
    except Exception as error:
        print('Error resuming demand:', str(error))
        return jsonify({
            'code': 1,
            'message': str(error)
        }), 500


# 中介分配与订单统计功能实现

# 从refund.py导入路由
from routes.refund import refund_bp

app.register_blueprint(refund_bp)


# 直接定义agent相关的路由
@app.route('/api/agents/available', methods=['GET'])
def get_all_available_agents():  # 修改函数名
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # 确保agents表存在并有数据
        try:
            cursor.execute("SHOW TABLES LIKE 'agents'")
            if not cursor.fetchone():
                # 如果表不存在，创建它
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS `agents` (
                      `agent_id` int(11) NOT NULL AUTO_INCREMENT,
                      `agent_name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
                      `contact_info` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
                      `status` tinyint(1) NOT NULL DEFAULT 1 COMMENT '1-活跃, 0-不活跃',
                      `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
                      `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                      PRIMARY KEY (`agent_id`)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
                """)
                
                # 插入一些测试数据
                cursor.execute("""
                    INSERT INTO agents (agent_name, contact_info, status)
                    VALUES 
                        ('测试中介1', 'test1@example.com', 1),
                        ('测试中介2', 'test2@example.com', 1),
                        ('测试中介3', 'test3@example.com', 1);
                """)
                conn.commit()
        except Exception as e:
            print("检查/创建agents表时出错:", e)
        
        # 获取所有活跃中介
        query = """
            SELECT agent_id, agent_name, contact_info, status
            FROM agents
            WHERE status = 1
            ORDER BY agent_name
        """
        cursor.execute(query)
        agents = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'code': 0,
            'message': 'success',
            'data': agents
        })
    except Exception as e:
        print('Error getting available agents:', str(e))
        return jsonify({
            'code': 1,
            'message': str(e)
        }), 500

# 需求关联的中介及订单统计 - 确保名称唯一
@app.route('/api/demands/<int:demand_id>/agents', methods=['GET'])
def get_demand_agents(demand_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        query = """
            SELECT 
                a.agent_id,
                a.agent_name,
                a.contact_info,
                o.order_id,
                o.order_number,
                o.target_count,
                o.actual_count,
                o.completion_rate,
                o.status
            FROM agents a
            INNER JOIN orders o ON a.agent_id = o.agent_id 
            WHERE o.demand_id = %s
            ORDER BY a.agent_name
        """
        cursor.execute(query, (demand_id,))
        agents = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'code': 0,
            'message': 'success',
            'data': agents
        })
    except Exception as e:
        print('Error getting demand agents:', str(e))
        return jsonify({
            'code': 1,
            'message': str(e)
        }), 500


# 分配中介
@app.route('/api/demands/<int:demand_id>/agents', methods=['POST'])
def assign_agent(demand_id):
    try:
        data = request.json
        agent_id = data.get('agent_id')
        target_count = data.get('target_count', 0)

        if not agent_id:
            return jsonify({
                'code': 1,
                'message': '请提供中介ID'
            }), 400

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # 检查需求是否存在
        cursor.execute("SELECT demand_id FROM demands WHERE demand_id = %s", (demand_id,))
        if not cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({
                'code': 1,
                'message': '需求不存在'
            }), 404

        # 检查中介是否存在
        cursor.execute("SELECT agent_id FROM agents WHERE agent_id = %s", (agent_id,))
        if not cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({
                'code': 1,
                'message': '中介不存在'
            }), 404

        # 检查是否已经分配过该中介
        cursor.execute(
            "SELECT order_id FROM orders WHERE demand_id = %s AND agent_id = %s",
            (demand_id, agent_id)
        )
        if cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({
                'code': 1,
                'message': '该中介已经分配过'
            }), 400

        # 生成订单号
        order_number = f"ORD-{demand_id}-{agent_id}-{int(time.time())}"

        # 创建订单
        insert_query = """
            INSERT INTO orders (demand_id, agent_id, order_number, target_count, actual_count, status)
            VALUES (%s, %s, %s, %s, 0, 1)
        """
        cursor.execute(insert_query, (demand_id, agent_id, order_number, target_count))

        conn.commit()
        order_id = cursor.lastrowid

        cursor.close()
        conn.close()

        return jsonify({
            'code': 0,
            'message': '中介分配成功',
            'data': {
                'order_id': order_id,
                'order_number': order_number
            }
        })
    except Exception as e:
        print('Error assigning agent:', str(e))
        return jsonify({
            'code': 1,
            'message': str(e)
        }), 500


# 移除中介
@app.route('/api/demands/<int:demand_id>/agents/<int:agent_id>', methods=['DELETE'])
def remove_agent(demand_id, agent_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # 删除订单记录
        delete_query = """
            DELETE FROM orders
            WHERE demand_id = %s AND agent_id = %s
        """
        cursor.execute(delete_query, (demand_id, agent_id))

        conn.commit()

        cursor.close()
        conn.close()

        return jsonify({
            'code': 0,
            'message': '中介移除成功'
        })
    except Exception as e:
        print('Error removing agent:', str(e))
        return jsonify({
            'code': 1,
            'message': str(e)
        }), 500


# 更新订单
@app.route('/api/orders/<int:order_id>', methods=['PUT'])
def update_order(order_id):
    try:
        data = request.json
        target_count = data.get('target_count')

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        update_query = """
            UPDATE orders
            SET target_count = %s
            WHERE order_id = %s
        """
        cursor.execute(update_query, (target_count, order_id))

        conn.commit()

        cursor.close()
        conn.close()

        return jsonify({
            'code': 0,
            'message': '订单更新成功'
        })
    except Exception as e:
        print('Error updating order:', str(e))
        return jsonify({
            'code': 1,
            'message': str(e)
        }), 500


# 获取中介的订单详情
@app.route('/api/demands/<int:demand_id>/agents/<int:agent_id>/orders', methods=['GET'])
def get_agent_orders(demand_id, agent_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        query = """
            SELECT 
                o.order_id,
                o.order_number,
                o.target_count,
                o.actual_count,
                o.completion_rate,
                o.status,
                o.created_at
            FROM orders o
            WHERE o.demand_id = %s AND o.agent_id = %s
        """
        cursor.execute(query, (demand_id, agent_id))
        orders = cursor.fetchall()

        cursor.close()
        conn.close()

        return jsonify({
            'code': 0,
            'message': 'success',
            'data': orders
        })
    except Exception as e:
        print('Error getting agent orders:', str(e))
        return jsonify({
            'code': 1,
            'message': str(e)
        }), 500


# 创建订单明细
@app.route('/api/orders', methods=['POST'])
def create_order_detail():
    try:
        data = request.json
        order_id = data.get('order_id')
        order_number = data.get('order_number')

        if not order_id or not order_number:
            return jsonify({
                'code': 1,
                'message': '请提供订单ID和订单号'
            }), 400

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # 获取订单信息
        cursor.execute(
            "SELECT order_id, demand_id, agent_id, target_count, actual_count FROM orders WHERE order_id = %s",
            (order_id,))
        order = cursor.fetchone()

        if not order:
            cursor.close()
            conn.close()
            return jsonify({
                'code': 1,
                'message': '订单不存在'
            }), 404

        # 创建订单明细
        insert_query = """
            INSERT INTO order_details (order_id, order_number, status)
            VALUES (%s, %s, 1)
        """
        cursor.execute(insert_query, (order_id, order_number))

        # 更新订单的实际完成数量
        new_actual_count = order['actual_count'] + 1

        update_query = """
            UPDATE orders
            SET actual_count = %s
            WHERE order_id = %s
        """
        cursor.execute(update_query, (new_actual_count, order_id))

        conn.commit()

        detail_id = cursor.lastrowid

        cursor.close()
        conn.close()

        return jsonify({
            'code': 0,
            'message': '订单创建成功',
            'data': {
                'detail_id': detail_id,
                'actual_count': new_actual_count,
                'target_count': order['target_count'],
                'completion_rate': (new_actual_count / order['target_count'] * 100) if order['target_count'] > 0 else 0
            }
        })
    except Exception as e:
        print('Error creating order detail:', str(e))
        return jsonify({
            'code': 1,
            'message': str(e)
        }), 500


# 获取需求的所有相关中介
@app.route('/api/demands/<int:demand_id>/available-agents', methods=['GET'])
def get_demand_available_agents(demand_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # 获取所有已分配给该需求的中介
        query = """
            SELECT DISTINCT a.agent_id, a.agent_name, a.contact_info
            FROM agents a
            JOIN orders o ON a.agent_id = o.agent_id
            WHERE o.demand_id = %s AND a.status = 1
            ORDER BY a.agent_name
        """
        cursor.execute(query, (demand_id,))
        agents = cursor.fetchall()

        cursor.close()
        conn.close()

        return jsonify({
            'code': 0,
            'message': 'success',
            'data': agents
        })
    except Exception as e:
        print('Error getting demand available agents:', str(e))
        return jsonify({
            'code': 1,
            'message': str(e)
        }), 500


# 修改API路径，避免与现有路由冲突
@app.route('/api/detail-agent-assign/<int:detail_id>', methods=['POST'])
def assign_agent_to_detail(detail_id):
    try:
        data = request.json
        print(f"分配中介请求数据: {data}, 明细ID: {detail_id}")
        
        agent_id = data.get('agent_id')
        
        if agent_id is None:
            return jsonify({
                'code': 1,
                'message': '请提供中介ID'
            }), 400
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # 检查明细是否存在
        cursor.execute('SELECT detail_id, demand_id, order_id FROM demand_details WHERE detail_id = %s', (detail_id,))
        detail = cursor.fetchone()
        
        if not detail:
            cursor.close()
            conn.close()
            return jsonify({
                'code': 1,
                'message': '明细不存在'
            }), 404
        
        demand_id = detail['demand_id']
        old_order_id = detail['order_id']
        
        print(f"明细信息: demand_id={demand_id}, old_order_id={old_order_id}")
        
        # 处理中介关联 - 查找或创建订单
        new_order_id = None
        if agent_id:
            # 先检查中介是否存在
            cursor.execute('SELECT agent_id FROM agents WHERE agent_id = %s', (agent_id,))
            agent = cursor.fetchone()
            
            if not agent:
                print(f"中介不存在: {agent_id}")
                # 尝试从accounts表查找
                try:
                    cursor.execute('SELECT id FROM accounts WHERE id = %s AND (role = "intermediary" OR account_type = "intermediary")', (agent_id,))
                    if not cursor.fetchone():
                        cursor.close()
                        conn.close()
                        return jsonify({
                            'code': 1,
                            'message': '指定的中介不存在'
                        }), 404
                    # 如果account存在但agent不存在，创建一个agent记录
                    cursor.execute('SELECT name, username FROM accounts WHERE id = %s', (agent_id,))
                    account = cursor.fetchone()
                    agent_name = account.get('name') or account.get('username') or f"中介{agent_id}"
                    
                    cursor.execute("""
                        INSERT INTO agents (agent_id, agent_name, status)
                        VALUES (%s, %s, 1)
                    """, (agent_id, agent_name))
                    print(f"已创建中介记录: agent_id={agent_id}, agent_name={agent_name}")
                except Exception as e:
                    print(f"检查/创建中介时出错: {e}")
            
            # 查找该需求下该中介的订单
            cursor.execute("""
                SELECT order_id FROM orders 
                WHERE demand_id = %s AND agent_id = %s
            """, (demand_id, agent_id))
            
            order_result = cursor.fetchone()
            
            if order_result:
                # 使用现有订单
                new_order_id = order_result['order_id']
                print(f"使用现有订单: order_id={new_order_id}")
            else:
                # 创建新订单
                try:
                    order_number = f"ORD-{demand_id}-{agent_id}-{int(time.time())}"
                    cursor.execute("""
                        INSERT INTO orders (demand_id, agent_id, order_number, target_count, actual_count, status)
                        VALUES (%s, %s, %s, 1, 0, 1)
                    """, (demand_id, agent_id, order_number))
                    new_order_id = cursor.lastrowid
                    print(f"创建新订单: order_id={new_order_id}, order_number={order_number}")
                except Exception as e:
                    print(f"创建订单失败: {e}")
                    # 查看订单表结构和约束
                    cursor.execute("DESCRIBE orders")
                    columns = cursor.fetchall()
                    print(f"订单表结构: {columns}")
        
        # 更新明细关联的订单
        print(f"更新明细订单关联: detail_id={detail_id}, new_order_id={new_order_id}")
        cursor.execute("""
            UPDATE demand_details 
            SET order_id = %s
            WHERE detail_id = %s
        """, (new_order_id, detail_id))
        
        # 处理订单统计
        # 减少旧订单的实际完成数量
        if old_order_id:
            try:
                cursor.execute("""
                    UPDATE orders 
                    SET actual_count = GREATEST(actual_count - 1, 0)
                    WHERE order_id = %s
                """, (old_order_id,))
                print(f"更新旧订单计数: order_id={old_order_id}")
                
                # 更新完成率
                cursor.execute("""
                    UPDATE orders 
                    SET completion_rate = (actual_count / NULLIF(target_count, 0)) * 100
                    WHERE order_id = %s
                """, (old_order_id,))
            except Exception as e:
                print(f"更新旧订单失败: {e}")
        
        # 增加新订单的实际完成数量
        if new_order_id:
            try:
                cursor.execute("""
                    UPDATE orders 
                    SET actual_count = actual_count + 1
                    WHERE order_id = %s
                """, (new_order_id,))
                print(f"更新新订单计数: order_id={new_order_id}")
                
                # 更新完成率
                cursor.execute("""
                    UPDATE orders 
                    SET completion_rate = (actual_count / NULLIF(target_count, 0)) * 100
                    WHERE order_id = %s
                """, (new_order_id,))
            except Exception as e:
                print(f"更新新订单失败: {e}")
        
        conn.commit()
        
        # 获取更新后的数据
        cursor.execute('''
            SELECT dd.*, a.agent_id, a.agent_name, ds.status_name
            FROM demand_details dd
            LEFT JOIN orders o ON dd.order_id = o.order_id
            LEFT JOIN agents a ON o.agent_id = a.agent_id
            LEFT JOIN demand_status ds ON dd.status = ds.status_id
            WHERE dd.detail_id = %s
        ''', (detail_id,))
        
        result = cursor.fetchone()
        print(f"更新后的明细数据: {result}")
        
        # 处理返回数据中的图片列表
        if result and result.get('review_images'):
            result['review_images'] = result['review_images'].split(',')
        else:
            result['review_images'] = []
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'code': 0,
            'message': '中介分配成功',
            'data': result
        })
        
    except Exception as error:
        print('分配中介失败:', str(error))
        return jsonify({
            'code': 1,
            'message': str(error)
        }), 500


# 添加测试路由来确认API服务正常
@app.route('/api/test', methods=['GET', 'POST'])
def test_api():
    return jsonify({
        'code': 0,
        'message': 'API服务正常',
        'method': request.method,
        'timestamp': time.time()
    })


# 检查API是否正常工作的测试路由
@app.route('/api/check-apis', methods=['GET'])
def check_apis():
    # 列出所有可用的路由
    rules = []
    for rule in app.url_map.iter_rules():
        rules.append({
            'endpoint': rule.endpoint,
            'methods': list(rule.methods),
            'path': str(rule)
        })

    return jsonify({
        'code': 0,
        'message': 'API检查',
        'data': {
            'total_routes': len(rules),
            'routes': rules
        }
    })


# 从accounts表获取中介用户
@app.route('/api/accounts/intermediaries', methods=['GET'])
def get_account_intermediaries():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # 检查accounts表结构
        try:
            cursor.execute("DESCRIBE accounts")
            columns = [column['Field'] for column in cursor.fetchall()]
            print("账户表结构:", columns)
        except Exception as e:
            print("查询表结构出错:", e)

        # 根据实际的accounts表结构调整查询
        # 假设accounts表有id/account_id, name/account_name/username, role/type等字段
        try:
            query = """
                SELECT * FROM accounts
                WHERE role = 'intermediary' OR type = 'intermediary' OR user_type = 'intermediary'
                ORDER BY name
            """
            cursor.execute(query)
            intermediaries = cursor.fetchall()
            print(f"找到 {len(intermediaries)} 个中介账户")
        except Exception as e:
            print("查询中介账户出错:", e)
            # 尝试备用查询
            try:
                query = """
                    SELECT * FROM accounts
                    WHERE account_type = 'intermediary'
                    ORDER BY account_name
                """
                cursor.execute(query)
                intermediaries = cursor.fetchall()
                print(f"备用查询找到 {len(intermediaries)} 个中介账户")
            except Exception as e2:
                print("备用查询也失败:", e2)
                intermediaries = []

        cursor.close()
        conn.close()

        # 如果是空列表，尝试从agents表获取
        if not intermediaries:
            try:
                conn = get_db_connection()
                cursor = conn.cursor(dictionary=True)
                cursor.execute("""
                    SELECT agent_id as id, agent_name as name, contact_info as contact, status
                    FROM agents
                    WHERE status = 1
                """)
                intermediaries = cursor.fetchall()
                cursor.close()
                conn.close()
                print(f"从agents表找到 {len(intermediaries)} 个中介")
            except Exception as e:
                print("从agents表获取中介失败:", e)

        return jsonify({
            'code': 0,
            'message': 'success',
            'data': intermediaries
        })
    except Exception as e:
        print('获取中介账户失败:', str(e))
        return jsonify({
            'code': 1,
            'message': str(e)
        }), 500


# 添加路由处理器来处理直接请求到 /api/demand-details 的POST请求
# 修复路由处理函数，解决日期解析和字段重复问题
@app.route('/api/demand-details', methods=['POST'])
def create_generic_demand_detail():
    """处理直接POST到/api/demand-details的请求"""
    try:
        data = request.json
        print("收到创建明细请求数据:", data)

        demand_id = data.get('demand_id')
        if not demand_id:
            return jsonify({
                'code': 1,
                'message': '需求ID缺失，无法创建明细'
            }), 400

        # 复制一份数据，避免修改原始请求数据
        detail_data = data.copy()

        # 处理日期时间格式 - 使用更灵活的方式处理日期
        if detail_data.get('order_time'):
            try:
                # 尝试直接使用传入的日期格式（通常是ISO格式）
                if isinstance(detail_data['order_time'], str):
                    # 判断是否已经是MySQL格式 (YYYY-MM-DD HH:MM:SS)
                    if re.match(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', detail_data['order_time']):
                        pass  # 已经是正确格式，不需要转换
                    else:
                        # 尝试按照常见格式解析
                        try:
                            # 尝试ISO格式 (前端通常发送这种格式)
                            date_obj = datetime.fromisoformat(detail_data['order_time'].replace('Z', '+00:00'))
                            detail_data['order_time'] = date_obj.strftime('%Y-%m-%d %H:%M:%S')
                        except:
                            try:
                                # 尝试HTTP日期格式
                                date_obj = datetime.strptime(detail_data['order_time'], '%a, %d %b %Y %H:%M:%S GMT')
                                detail_data['order_time'] = date_obj.strftime('%Y-%m-%d %H:%M:%S')
                            except:
                                # 如果都失败，使用当前时间
                                detail_data['order_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            except Exception as e:
                print(f"处理order_time出错: {e}")
                detail_data['order_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        if detail_data.get('review_time'):
            try:
                if isinstance(detail_data['review_time'], str):
                    if re.match(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', detail_data['review_time']):
                        pass  # 已经是正确格式
                    else:
                        try:
                            # 尝试ISO格式
                            date_obj = datetime.fromisoformat(detail_data['review_time'].replace('Z', '+00:00'))
                            detail_data['review_time'] = date_obj.strftime('%Y-%m-%d %H:%M:%S')
                        except:
                            try:
                                # 尝试HTTP日期格式
                                date_obj = datetime.strptime(detail_data['review_time'], '%a, %d %b %Y %H:%M:%S GMT')
                                detail_data['review_time'] = date_obj.strftime('%Y-%m-%d %H:%M:%S')
                            except:
                                detail_data['review_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            except Exception as e:
                print(f"处理review_time出错: {e}")
                detail_data['review_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # 处理图片列表
        if isinstance(detail_data.get('review_images'), list):
            detail_data['review_images'] = ','.join([str(img) for img in detail_data['review_images'] if img])

        # 连接数据库
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # 检查需求是否存在
        cursor.execute("SELECT demand_id FROM demands WHERE demand_id = %s", (demand_id,))
        if not cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({
                'code': 1,
                'message': '需求不存在'
            }), 404

        # 从数据中提取agent_id并移除，避免SQL错误
        agent_id = detail_data.pop('agent_id', None)

        # 准备插入字段和值，确保demand_id不重复
        # 先移除可能存在的demand_id，稍后再添加
        if 'demand_id' in detail_data:
            detail_data.pop('demand_id')

        # 构建字段列表和值列表
        fields = list(detail_data.keys())
        values = [detail_data[field] for field in fields]

        # 添加demand_id
        fields.append('demand_id')
        values.append(demand_id)

        # 处理中介关联
        order_id = None
        if agent_id:
            # 查找该需求下该中介的订单
            cursor.execute("""
                SELECT order_id FROM orders 
                WHERE demand_id = %s AND agent_id = %s
            """, (demand_id, agent_id))

            order_result = cursor.fetchone()

            if order_result:
                # 使用现有订单
                order_id = order_result['order_id']
            else:
                # 创建新订单
                order_number = f"ORD-{demand_id}-{agent_id}-{int(time.time())}"
                cursor.execute("""
                    INSERT INTO orders (demand_id, agent_id, order_number, target_count, actual_count, status)
                    VALUES (%s, %s, %s, 1, 0, 1)
                """, (demand_id, agent_id, order_number))
                order_id = cursor.lastrowid

        # 如果关联了订单，添加order_id字段
        if order_id:
            fields.append('order_id')
            values.append(order_id)

        # 构建INSERT语句
        placeholders = ', '.join(['%s'] * len(values))
        insert_query = f"""
            INSERT INTO demand_details ({', '.join(fields)})
            VALUES ({placeholders})
        """

        print("执行SQL:", insert_query)
        print("SQL参数:", values)

        cursor.execute(insert_query, values)
        detail_id = cursor.lastrowid

        # 如果关联了订单，更新订单统计
        if order_id:
            cursor.execute("""
                UPDATE orders 
                SET actual_count = actual_count + 1,
                    completion_rate = (actual_count + 1) / target_count * 100
                WHERE order_id = %s
            """, (order_id,))

        # 获取创建的详情
        cursor.execute('''
            SELECT dd.*, a.agent_id, a.agent_name, ds.status_name
            FROM demand_details dd
            LEFT JOIN orders o ON dd.order_id = o.order_id
            LEFT JOIN agents a ON o.agent_id = a.agent_id
            LEFT JOIN demand_status ds ON dd.status = ds.status_id
            WHERE dd.detail_id = %s
        ''', (detail_id,))

        result = cursor.fetchone()

        # 处理返回数据中的图片列表
        if result and result.get('review_images'):
            result['review_images'] = result['review_images'].split(',')
        else:
            result['review_images'] = []

        # 处理数值字段
        if result and result.get('order_amount'):
            result['order_amount'] = float(result['order_amount'])

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({
            'code': 0,
            'message': '创建成功',
            'data': result
        })

    except Exception as error:
        print('Error creating demand detail:', str(error))
        return jsonify({
            'code': 1,
            'message': str(error)
        }), 500
# 添加调试端点，记录所有请求
@app.route('/api/debug', methods=['GET', 'POST', 'PUT', 'DELETE'])
def debug_api():
    print(f"收到 {request.method} 请求: {request.url}")
    print(f"请求数据: {request.get_data(as_text=True)}")
    print(f"请求头: {dict(request.headers)}")

    return jsonify({
        'code': 0,
        'message': '调试信息已记录',
        'data': {
            'method': request.method,
            'url': request.url,
            'headers': dict(request.headers),
            'data': request.get_json(silent=True)
        }
    })

# 添加帮助函数检查表结构
@app.route('/api/check-table/<table_name>', methods=['GET'])
def check_table_structure(table_name):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # 获取表结构
        cursor.execute(f"DESCRIBE {table_name}")
        columns = cursor.fetchall()
        
        # 获取表数据示例
        cursor.execute(f"SELECT * FROM {table_name} LIMIT 1")
        sample = cursor.fetchone()
        
        # 获取表行数
        cursor.execute(f"SELECT COUNT(*) as count FROM {table_name}")
        count = cursor.fetchone()['count']
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'code': 0,
            'message': f'表 {table_name} 结构检查',
            'data': {
                'columns': columns,
                'sample': sample,
                'count': count
            }
        })
    except Exception as e:
        return jsonify({
            'code': 1,
            'message': f'检查表 {table_name} 失败: {str(e)}'
        }), 500

# 启动服务器
if __name__ == '__main__':
    try:
        # 确保上传目录存在并设置权限
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        os.chmod(app.config['UPLOAD_FOLDER'], 0o755)
            
        # 检查目录权限
        if not os.access(app.config['UPLOAD_FOLDER'], os.W_OK):
            print('Warning: Upload directory is not writable')

        
        # 启动应用
        app.run(host='0.0.0.0', port=5000, debug=True)
    except Exception as error:
        print('Server startup failed:', str(error))
        exit(1) 


