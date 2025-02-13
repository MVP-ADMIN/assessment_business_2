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

# CORS 配置
cors_options = {
    "origins": ["http://localhost:5173", "http://127.0.0.1:5173"],
    "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    "allow_headers": [
        "Content-Type", 
        "Accept", 
        "Authorization", 
        "X-Requested-With",
        "X-Token",
        "X-Username",
        "X-Password"
    ],
    "expose_headers": [
        "Content-Length", 
        "Content-Type", 
        "Authorization",
        "X-Token"
    ],
    "supports_credentials": True
}
CORS(app, resources={
    r"/api/*": cors_options,
    r"/basic-api/*": cors_options,  # 添加 basic-api 路径的 CORS 配置
    r"/uploads/*": cors_options     # 添加 uploads 路径的 CORS 配置
})

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

# 创建测评明细
@app.route('/api/demand-details', methods=['POST'])
def create_demand_detail():
    try:
        data = request.json
        print("Received data:", data)  # 添加日志
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # 处理可能为 None 的字段
        review_time = data.get('review_time') or None
        
        # 确保 review_images 是列表并且所有元素都是字符串
        review_images = data.get('review_images', [])
        if review_images and isinstance(review_images, list):
            review_images = [str(img) for img in review_images if img]
            review_images = ','.join(review_images) if review_images else None
        else:
            review_images = None
            
        review_video = data.get('review_video') or None
        payment_screenshot = data.get('payment_screenshot') or None
        order_screenshot = data.get('order_screenshot') or None
        review_screenshot = data.get('review_screenshot') or None
        remark = data.get('remark') or None
        
        # 打印处理后的数据
        print("Processed data:", {
            'review_time': review_time,
            'review_images': review_images,
            'review_video': review_video,
            'payment_screenshot': payment_screenshot,
            'order_screenshot': order_screenshot,
            'review_screenshot': review_screenshot,
            'remark': remark
        })
        
        # 插入明细数据
        insert_query = '''
            INSERT INTO demand_details (
                demand_id, order_number, order_amount, order_time,
                review_content, review_time, review_images, review_video,
                payment_screenshot, order_screenshot, review_screenshot,
                status, remark
            ) VALUES (
                %(demand_id)s, %(order_number)s, %(order_amount)s, %(order_time)s,
                %(review_content)s, %(review_time)s, %(review_images)s, %(review_video)s,
                %(payment_screenshot)s, %(order_screenshot)s, %(review_screenshot)s,
                %(status)s, %(remark)s
            )
        '''
        
        insert_data = {
            'demand_id': data['demand_id'],
            'order_number': data['order_number'],
            'order_amount': data['order_amount'],
            'order_time': data['order_time'],
            'review_content': data.get('review_content'),
            'review_time': review_time,
            'review_images': review_images,
            'review_video': review_video,
            'payment_screenshot': payment_screenshot,
            'order_screenshot': order_screenshot,
            'review_screenshot': review_screenshot,
            'status': data.get('status', 1),  # 默认状态为1
            'remark': remark
        }
        
        # 打印最终的插入数据
        print("Insert data:", insert_data)
        
        cursor.execute(insert_query, insert_data)
        detail_id = cursor.lastrowid
        
        # 获取插入的数据
        cursor.execute('SELECT * FROM demand_details WHERE detail_id = %s', (detail_id,))
        result = cursor.fetchone()
        
        # 处理返回数据中的图片列表
        if result and result.get('review_images'):
            result['review_images'] = result['review_images'].split(',')
        else:
            result['review_images'] = []
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            'code': 0,  # 确保成功时返回 code: 0
            'message': 'Detail created successfully',
            'data': result
        })
        
    except Exception as error:
        print('Error creating demand detail:', str(error))
        print('Request data:', request.json)  # 添加请求数据日志
        return jsonify({
            'code': 1,
            'message': str(error)
        }), 500

# 获取需求明细列表
@app.route('/api/demands/<int:demand_id>/details', methods=['GET'])
def get_demand_details(demand_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # 检查需求是否存在
        cursor.execute('SELECT demand_id FROM demands WHERE demand_id = %s', (demand_id,))
        if not cursor.fetchone():
            return jsonify({
                'code': 1,
                'message': '需求不存在'
            }), 404
            
        # 获取明细列表
        cursor.execute('''
            SELECT 
                dd.*,
                ds.status_name
            FROM demand_details dd
            LEFT JOIN demand_status ds ON dd.status = ds.status_id
            WHERE dd.demand_id = %s 
            ORDER BY dd.created_at DESC
        ''', (demand_id,))
        
        rows = cursor.fetchall()
        
        # 处理图片列表
        for row in rows:
            if row.get('review_images'):
                row['review_images'] = row['review_images'].split(',')
            else:
                row['review_images'] = []
                
            # 处理数值字段
            row['order_amount'] = float(row['order_amount'] or 0)
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'code': 0,
            'message': 'success',
            'data': rows
        })
        
    except Exception as error:
        print('Error fetching demand details:', str(error))
        return jsonify({
            'code': 1,
            'message': str(error)
        }), 500

# 获取单个测评明细
@app.route('/api/demand-details/<int:detail_id>', methods=['GET'])
def get_demand_detail(detail_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute('''
            SELECT 
                dd.*,
                ds.status_name
            FROM demand_details dd
            LEFT JOIN demand_status ds ON dd.status = ds.status_id
            WHERE dd.detail_id = %s
        ''', (detail_id,))
        
        result = cursor.fetchone()
        
        if not result:
            return jsonify({
                'code': 1,
                'message': '明细不存在'
            }), 404
            
        # 处理图片列表
        if result.get('review_images'):
            result['review_images'] = result['review_images'].split(',')
        else:
            result['review_images'] = []
            
        # 处理数值字段
        result['order_amount'] = float(result['order_amount'] or 0)
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'code': 0,
            'message': 'success',
            'data': result
        })
        
    except Exception as error:
        print('Error fetching demand detail:', str(error))
        return jsonify({
            'code': 1,
            'message': str(error)
        }), 500

# 更新测评明细
@app.route('/api/demand-details/<int:detail_id>', methods=['PUT'])
def update_demand_detail(detail_id):
    try:
        data = request.json
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # 检查明细是否存在
        cursor.execute('SELECT detail_id FROM demand_details WHERE detail_id = %s', (detail_id,))
        if not cursor.fetchone():
            return jsonify({
                'code': 1,
                'message': '明细不存在'
            }), 404
        
        # 处理图片列表
        if isinstance(data.get('review_images'), list):
            data['review_images'] = ','.join(data['review_images'])
            
        # 处理日期时间格式
        if data.get('order_time'):
            try:
                # 将时间字符串转换为datetime对象，然后格式化为MySQL格式
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
        
        # 构建更新语句
        update_fields = []
        update_values = {}
        
        # 只更新允许的字段
        allowed_fields = [
            'order_number', 'order_amount', 'order_time',
            'review_content', 'review_time', 'review_images', 'review_video',
            'payment_screenshot', 'order_screenshot', 'review_screenshot',
            'status', 'remark'
        ]
        
        for key in allowed_fields:
            if key in data:
                update_fields.append(f'{key} = %({key})s')
                update_values[key] = data[key]
                
        update_values['detail_id'] = detail_id
        
        if not update_fields:
            return jsonify({
                'code': 1,
                'message': '没有需要更新的字段'
            }), 400
        
        # 打印更新数据用于调试
        print("Update values:", update_values)
        
        update_query = f'''
            UPDATE demand_details 
            SET {', '.join(update_fields)}
            WHERE detail_id = %(detail_id)s
        '''
        
        cursor.execute(update_query, update_values)
        
        # 获取更新后的数据
        cursor.execute('''
            SELECT dd.*
            FROM demand_details dd
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
            'message': 'success',
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


# 启动服务器
if __name__ == '__main__':
    try:
        # 确保上传目录存在并设置权限
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        os.chmod(app.config['UPLOAD_FOLDER'], 0o755)
            
        # 检查目录权限
        if not os.access(app.config['UPLOAD_FOLDER'], os.W_OK):
            print('Warning: Upload directory is not writable')
        
        # 注册蓝图
        app.register_blueprint(refund_bp)
        
        # 启动应用
        app.run(host='0.0.0.0', port=5000, debug=True)
    except Exception as error:
        print('Server startup failed:', str(error))
        exit(1) 

@app.route('/api/demands/<int:id>/pause', methods=['PUT'])
def pause_demand(id):
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
            'message': 'success'
        })
        
    except Exception as error:
        print('Error pausing demand:', str(error))
        return jsonify({
            'code': 1,
            'message': str(error)
        }), 500

@app.route('/api/demands/<int:id>/resume', methods=['PUT'])
def resume_demand(id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # 更新需求状态为进行中
        cursor.execute("""
            UPDATE demands 
            SET status_id = 2 
            WHERE demand_id = %s
        """, (id,))
        
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

