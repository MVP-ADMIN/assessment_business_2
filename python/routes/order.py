from flask import Blueprint, request, jsonify
from db import get_db_connection
import time

order_bp = Blueprint('order', __name__)

# 创建订单
@order_bp.route('/api/orders', methods=['POST'])
def create_order():
    try:
        data = request.json
        demand_id = data.get('demand_id')
        agent_id = data.get('agent_id')
        order_number = data.get('order_number')
        
        if not all([demand_id, agent_id, order_number]):
            return jsonify({
                'code': 1,
                'message': '请提供需求ID、中介ID和订单号'
            }), 400
            
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # 检查中介与需求的关联是否存在
        cursor.execute(
            "SELECT order_id, actual_count, target_count FROM orders WHERE demand_id = %s AND agent_id = %s", 
            (demand_id, agent_id)
        )
        order = cursor.fetchone()
        
        if not order:
            return jsonify({
                'code': 1,
                'message': '中介未分配给此需求'
            }), 400
            
        # 增加实际完成数量
        new_actual_count = order['actual_count'] + 1
        
        # 更新订单
        update_query = """
            UPDATE orders
            SET actual_count = %s
            WHERE demand_id = %s AND agent_id = %s
        """
        cursor.execute(update_query, (new_actual_count, demand_id, agent_id))
        
        # 添加订单明细
        insert_detail_query = """
            INSERT INTO order_details 
            (order_id, order_number, status, created_at) 
            VALUES (%s, %s, 1, NOW())
        """
        cursor.execute(insert_detail_query, (order['order_id'], order_number))
        
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
                'completion_rate': (new_actual_count / order['target_count']) * 100
            }
        })
    except Exception as e:
        print('Error creating order:', str(e))
        return jsonify({
            'code': 1,
            'message': str(e)
        }), 500

# 删除订单
@order_bp.route('/api/orders/<int:order_id>', methods=['DELETE'])
def delete_order(order_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # 获取订单信息
        cursor.execute("SELECT order_id, demand_id, agent_id, actual_count FROM orders WHERE order_id = %s", (order_id,))
        order = cursor.fetchone()
        
        if not order:
            return jsonify({
                'code': 1,
                'message': '订单不存在'
            }), 404
            
        # 减少实际完成数量
        new_actual_count = max(0, order['actual_count'] - 1)
        
        # 更新订单
        update_query = """
            UPDATE orders
            SET actual_count = %s
            WHERE order_id = %s
        """
        cursor.execute(update_query, (new_actual_count, order_id))
        
        conn.commit()
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'code': 0,
            'message': '订单删除成功'
        })
    except Exception as e:
        print('Error deleting order:', str(e))
        return jsonify({
            'code': 1,
            'message': str(e)
        }), 500 