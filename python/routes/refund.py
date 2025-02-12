from flask import Blueprint, request, jsonify
from db import get_db_connection
from datetime import datetime
import pytz

# 创建蓝图
refund_bp = Blueprint('refund', __name__)

# 返款订单相关API
@refund_bp.route('/api/refund/orders', methods=['GET'])
def list_refund_orders():
    try:
        page = int(request.args.get('page', 1))
        size = int(request.args.get('size', 20))
        keyword = request.args.get('keyword', '')
        status = request.args.get('status')
        
        offset = (page - 1) * size
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # 构建查询条件
        where_clause = []
        params = []
        
        if keyword:
            where_clause.append("""
                (ro.order_number LIKE %s 
                OR d.marketing_number LIKE %s)
            """)
            params.extend([f'%{keyword}%'] * 2)
            
        if status:
            where_clause.append('ro.status = %s')
            params.append(status)
            
        where_sql = ' AND '.join(where_clause) if where_clause else '1=1'
        
        # 查询总数
        count_sql = f"""
            SELECT COUNT(*) as total 
            FROM refund_orders ro
            LEFT JOIN demands d ON ro.demand_id = d.demand_id
            LEFT JOIN refund_payments rp ON ro.id = rp.order_id
            WHERE {where_sql}
        """
        cursor.execute(count_sql, params)
        total = cursor.fetchone()['total']
        
        # 查询数据
        query = f"""
            SELECT 
                ro.id,
                ro.order_number,
                ro.order_date,
                ro.order_amount,
                ro.currency,
                ro.status,
                d.marketing_number,
                d.dingtalk_number,
                rp.customer_email,
                rp.transfer_amount,
                rp.payment_method,
                rp.payment_time,
                rp.payment_screenshot
            FROM refund_orders ro
            LEFT JOIN demands d ON ro.demand_id = d.demand_id
            LEFT JOIN refund_payments rp ON ro.id = rp.order_id
            WHERE {where_sql}
            ORDER BY ro.created_at DESC
            LIMIT %s OFFSET %s
        """
        cursor.execute(query, params + [size, offset])
        items = cursor.fetchall()
        
        # 处理日期格式
        for item in items:
            if item.get('order_date'):
                item['order_date'] = item['order_date'].strftime('%Y-%m-%d %H:%M:%S')
            if item.get('payment_time'):
                item['payment_time'] = item['payment_time'].strftime('%Y-%m-%d %H:%M:%S')
        
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

@refund_bp.route('/api/refund/orders/search', methods=['GET'])
def search_refund_demands():
    try:
        keyword = request.args.get('keyword', '')
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        query = """
            SELECT 
                d.demand_id,
                d.marketing_number,
                d.dingtalk_number,
                d.asin,
                dd.detail_id,
                dd.order_number,
                dd.order_amount,
                dd.order_time
            FROM demands d
            LEFT JOIN demand_details dd ON d.demand_id = dd.demand_id
            WHERE d.marketing_number LIKE %s 
                OR dd.order_number LIKE %s
                AND dd.order_amount > 0  -- 只查询有订单金额的记录
            ORDER BY d.registration_date DESC
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
        print('Error searching demands:', str(error))
        return jsonify({
            'code': 1,
            'message': str(error)
        }), 500

@refund_bp.route('/api/refund/orders', methods=['POST'])
def create_refund_order():
    try:
        data = request.json
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # 检查必填字段
        required_fields = ['demand_id', 'detail_id', 'order_amount', 'currency', 'business_type']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({
                    'code': 1,
                    'message': f'Missing required field: {field}'
                }), 400

        # 获取需求和明细信息
        cursor.execute("""
            SELECT 
                d.marketing_number,
                d.dingtalk_number,
                d.asin,
                dd.order_number,
                dd.order_time
            FROM demands d
            LEFT JOIN demand_details dd ON d.demand_id = dd.demand_id
            WHERE d.demand_id = %s AND dd.detail_id = %s
        """, (data['demand_id'], data['detail_id']))
        
        base_info = cursor.fetchone()
        if not base_info:
            return jsonify({
                'code': 1,
                'message': 'Invalid demand_id or detail_id'
            }), 400

        # 合并基础信息
        insert_data = {
            **data,
            'marketing_number': base_info['marketing_number'],
            'dingtalk_number': base_info['dingtalk_number'],
            'asin': base_info['asin'],
            'order_number': base_info['order_number'],
            'order_time': base_info['order_time'],
            'status': 'pending'
        }

        # 插入订单数据
        insert_sql = """
            INSERT INTO refund_orders (
                demand_id, detail_id, marketing_number, dingtalk_number,
                asin, order_number, order_time, order_amount,
                currency, business_type, payment_method,
                paypal_principal, rmb_commission, intermediary_commission,
                commission_currency, exchange_rate, actual_payment, status
            ) VALUES (
                %(demand_id)s, %(detail_id)s, %(marketing_number)s, %(dingtalk_number)s,
                %(asin)s, %(order_number)s, %(order_time)s, %(order_amount)s,
                %(currency)s, %(business_type)s, %(payment_method)s,
                %(paypal_principal)s, %(rmb_commission)s, %(intermediary_commission)s,
                %(commission_currency)s, %(exchange_rate)s, %(actual_payment)s, %(status)s
            )
        """
        cursor.execute(insert_sql, insert_data)
        order_id = cursor.lastrowid
        
        # 记录日志
        log_sql = """
            INSERT INTO refund_logs (
                order_id, action, new_status, operator, remark
            ) VALUES (%s, 'create', 'pending', %s, %s)
        """
        cursor.execute(log_sql, (
            order_id, 
            data.get('operator', 'system'),
            '创建返款订单'
        ))
        
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

@refund_bp.route('/api/refunds/payments', methods=['POST'])
def create_refund_payment():
    conn = None
    cursor = None
    try:
        data = request.json
        print("Received payment data:", data)
        
        # 转换时间格式
        try:
            # 解析 ISO 格式的时间字符串
            payment_time = data['payment_time'].replace('Z', '+00:00')
            dt = datetime.fromisoformat(payment_time)
            # 转换为本地时间
            local_dt = dt.astimezone(pytz.timezone('Asia/Shanghai'))
            # 格式化为 MySQL datetime 格式
            formatted_time = local_dt.strftime('%Y-%m-%d %H:%M:%S')
            data['payment_time'] = formatted_time
        except Exception as e:
            print("Error parsing payment time:", str(e))
            return jsonify({
                'code': 1,
                'message': '支付时间格式错误'
            }), 400

        # 验证订单号格式
        if not data.get('order_number'):
            return jsonify({
                'code': 1,
                'message': '订单号不能为空'
            }), 400

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # 先检查订单号是否存在于测评明细中
        check_sql = """
            SELECT COUNT(*) as count 
            FROM demand_details 
            WHERE order_number = %s
        """
        cursor.execute(check_sql, (data['order_number'],))
        result = cursor.fetchone()
        
        if not result or result['count'] == 0:
            return jsonify({
                'code': 1,
                'message': '订单号不存在于测评明细列表中'
            }), 400

        # 获取订单详细信息
        detail_sql = """
            SELECT 
                dd.demand_id,
                dd.detail_id,
                dd.order_number,
                dd.order_amount,
                d.marketing_number,
                d.dingtalk_number,
                d.asin
            FROM demand_details dd
            LEFT JOIN demands d ON dd.demand_id = d.demand_id
            WHERE dd.order_number = %s
        """
        cursor.execute(detail_sql, (data['order_number'],))
        detail = cursor.fetchone()
        
        if not detail:
            return jsonify({
                'code': 1,
                'message': '无法获取订单详细信息'
            }), 400

        # 检查返款订单是否已存在
        order_sql = """
            SELECT id, detail_id 
            FROM refund_orders 
            WHERE order_number = %s
        """
        cursor.execute(order_sql, (data['order_number'],))
        refund_order = cursor.fetchone()

        try:
            if refund_order:
                order_id = refund_order['id']
                detail_id = refund_order['detail_id']
                print("Using existing refund order:", order_id)
            else:
                # 创建新的返款订单
                insert_order_sql = """
                    INSERT INTO refund_orders (
                        demand_id, detail_id, marketing_number, dingtalk_number,
                        asin, order_number, order_amount, currency,
                        business_type, status, order_date
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, 
                        'joint', 'pending', NOW()
                    )
                """
                cursor.execute(insert_order_sql, (
                    detail['demand_id'],
                    detail['detail_id'],
                    detail['marketing_number'],
                    detail['dingtalk_number'],
                    detail['asin'],
                    detail['order_number'],
                    data['order_amount'],
                    data['currency']
                ))
                conn.commit()
                order_id = cursor.lastrowid
                detail_id = detail['detail_id']
                print("Created new refund order:", order_id)

            # 创建支付记录
            payment_sql = """
                INSERT INTO refund_payments (
                    order_id, detail_id, customer_email, order_amount,
                    transfer_amount, currency, intermediary_commission,
                    commission_currency, rmb_commission, payment_method,
                    payment_account, payment_time, payment_screenshot,
                    remark, status
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, 'pending'
                )
            """
            payment_data = (
                order_id,
                detail_id,
                data['customer_email'],
                data['order_amount'],
                data['transfer_amount'],
                data['currency'],
                data.get('intermediary_commission', 0),
                data.get('commission_currency'),
                data.get('rmb_commission', 0),
                data['payment_method'],
                data['payment_account'],
                data['payment_time'],
                data['payment_screenshot'],
                data.get('remark', '')
            )
            cursor.execute(payment_sql, payment_data)
            payment_id = cursor.lastrowid

            # 更新订单状态
            cursor.execute("""
                UPDATE refund_orders 
                SET status = 'completed'
                WHERE id = %s
            """, (order_id,))

            # 记录日志
            cursor.execute("""
                INSERT INTO refund_logs (
                    order_id, action, old_status, new_status, operator, remark
                ) VALUES (%s, 'payment', 'pending', 'completed', %s, %s)
            """, (order_id, 'system', '创建返款支付记录'))

            conn.commit()
            print("Successfully created payment record:", payment_id)

            return jsonify({
                'code': 0,
                'message': 'success',
                'data': {'id': payment_id}
            })

        except Exception as e:
            print("Error during database operations:", str(e))
            conn.rollback()
            raise

    except Exception as error:
        print("Error creating refund payment:", str(error))
        print("Request data:", data)
        return jsonify({
            'code': 1,
            'message': f'创建支付记录失败: {str(error)}'
        }), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# 添加最近返款记录接口
@refund_bp.route('/api/refunds/recent', methods=['GET'])
def get_recent_refunds():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # 查询最近的返款记录
        query = """
            SELECT 
                ro.id,
                ro.order_number,
                ro.order_date,
                ro.order_amount,
                ro.currency,
                ro.status,
                d.marketing_number,
                d.dingtalk_number,
                rp.customer_email,
                rp.transfer_amount,
                rp.payment_method,
                rp.payment_time,
                rp.payment_screenshot
            FROM refund_orders ro
            LEFT JOIN demands d ON ro.demand_id = d.demand_id
            LEFT JOIN refund_payments rp ON ro.id = rp.order_id
            ORDER BY ro.created_at DESC
            LIMIT 10
        """
        cursor.execute(query)
        items = cursor.fetchall()
        
        # 处理日期格式
        for item in items:
            if item.get('order_date'):
                item['order_date'] = item['order_date'].strftime('%Y-%m-%d %H:%M:%S')
            if item.get('payment_time'):
                item['payment_time'] = item['payment_time'].strftime('%Y-%m-%d %H:%M:%S')
        
        print("Returning items:", items)  # 添加调试日志
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'code': 0,
            'message': 'success',
            'data': items
        })
        
    except Exception as error:
        print('Error getting recent refunds:', str(error))
        return jsonify({
            'code': 1,
            'message': str(error)
        }), 500 