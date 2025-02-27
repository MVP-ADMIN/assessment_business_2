from flask import Blueprint, request, jsonify
from db import get_db_connection
import time

agent_bp = Blueprint('agent', __name__)

# 获取所有可用中介
@agent_bp.route('/api/agents/available', methods=['GET'])
def get_available_agents():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
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

# 获取需求关联的中介及订单统计
@agent_bp.route('/api/demands/<int:demand_id>/agents', methods=['GET'])
def get_demand_agents(demand_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        query = """
            SELECT 
                a.agent_id,
                a.agent_name,
                COUNT(o.order_id) as total_orders,
                SUM(CASE WHEN o.status = 2 THEN 1 ELSE 0 END) as completed_orders,
                o.target_count,
                o.actual_count,
                o.completion_rate
            FROM agents a
            JOIN orders o ON a.agent_id = o.agent_id
            WHERE o.demand_id = %s
            GROUP BY a.agent_id, a.agent_name, o.target_count, o.actual_count, o.completion_rate
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

# 分配中介到需求
@agent_bp.route('/api/demands/<int:demand_id>/agents', methods=['POST'])
def assign_agent(demand_id):
    try:
        data = request.json
        agent_id = data.get('agent_id')
        target_count = data.get('target_count', 1)
        
        if not agent_id:
            return jsonify({
                'code': 1,
                'message': '请选择中介'
            }), 400
            
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # 检查需求是否存在
        cursor.execute("SELECT demand_id FROM demands WHERE demand_id = %s", (demand_id,))
        if not cursor.fetchone():
            return jsonify({
                'code': 1,
                'message': '需求不存在'
            }), 404
            
        # 检查中介是否存在
        cursor.execute("SELECT agent_id FROM agents WHERE agent_id = %s", (agent_id,))
        if not cursor.fetchone():
            return jsonify({
                'code': 1,
                'message': '中介不存在'
            }), 404
            
        # 检查是否已经分配过
        cursor.execute(
            "SELECT order_id FROM orders WHERE demand_id = %s AND agent_id = %s", 
            (demand_id, agent_id)
        )
        if cursor.fetchone():
            return jsonify({
                'code': 1,
                'message': '该中介已分配给此需求'
            }), 400
            
        # 创建订单记录
        insert_query = """
            INSERT INTO orders 
            (demand_id, agent_id, order_number, target_count, actual_count, status) 
            VALUES (%s, %s, %s, %s, 0, 1)
        """
        order_number = f"ORD-{demand_id}-{agent_id}-{int(time.time())}"
        cursor.execute(insert_query, (demand_id, agent_id, order_number, target_count))
        conn.commit()
        
        order_id = cursor.lastrowid
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'code': 0,
            'message': '分配成功',
            'data': {
                'order_id': order_id
            }
        })
    except Exception as e:
        print('Error assigning agent:', str(e))
        return jsonify({
            'code': 1,
            'message': str(e)
        }), 500

# 获取中介的订单详情
@agent_bp.route('/api/demands/<int:demand_id>/agents/<int:agent_id>/orders', methods=['GET'])
def get_agent_orders(demand_id, agent_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        query = """
            SELECT 
                o.order_id,
                o.order_number,
                o.status,
                o.created_at,
                o.updated_at
            FROM orders o
            WHERE o.demand_id = %s AND o.agent_id = %s
            ORDER BY o.created_at DESC
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

# 移除分配的中介
@agent_bp.route('/api/demands/<int:demand_id>/agents/<int:agent_id>', methods=['DELETE'])
def remove_agent(demand_id, agent_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # 删除中介关联的订单
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
            'message': '移除成功'
        })
    except Exception as e:
        print('Error removing agent:', str(e))
        return jsonify({
            'code': 1,
            'message': str(e)
        }), 500 