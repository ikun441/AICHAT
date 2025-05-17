import json
import os
import sqlite3
from typing import Dict, Any, List, Optional, Union
import logging

logger = logging.getLogger(__name__)


class Database:
    """数据库操作类，负责数据存储和检索"""
    
    def __init__(self, db_path: str = "database/app.db"):
        """初始化数据库
        
        Args:
            db_path: 数据库文件路径
        """
        self.db_path = db_path
        self._ensure_db_dir()
        self._init_db()
    
    def _ensure_db_dir(self):
        """确保数据库目录存在"""
        db_dir = os.path.dirname(self.db_path)
        if not os.path.exists(db_dir):
            os.makedirs(db_dir)
    
    def _init_db(self):
        """初始化数据库表结构"""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            
            # 用户表
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                username TEXT NOT NULL,
                status TEXT DEFAULT 'active',
                is_ai BOOLEAN DEFAULT 1,
                eliminated BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            
            # 好友关系表
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS friendships (
                user_id TEXT,
                friend_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (user_id, friend_id),
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (friend_id) REFERENCES users (id)
            )
            ''')
            
            # 群组表
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS groups (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                created_by TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (created_by) REFERENCES users (id)
            )
            ''')
            
            # 群组成员表
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS group_members (
                group_id TEXT,
                user_id TEXT,
                joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (group_id, user_id),
                FOREIGN KEY (group_id) REFERENCES groups (id),
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
            ''')
            
            # 私聊消息表
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS private_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sender_id TEXT,
                receiver_id TEXT,
                content TEXT,
                sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (sender_id) REFERENCES users (id),
                FOREIGN KEY (receiver_id) REFERENCES users (id)
            )
            ''')
            
            # 群聊消息表
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS group_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                group_id TEXT,
                sender_id TEXT,
                content TEXT,
                sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (group_id) REFERENCES groups (id),
                FOREIGN KEY (sender_id) REFERENCES users (id)
            )
            ''')
            
            # 投票表
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS votes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                voter_id TEXT,
                target_id TEXT,
                round INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (voter_id) REFERENCES users (id),
                FOREIGN KEY (target_id) REFERENCES users (id)
            )
            ''')
            
            # 遗言表
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS last_words (
                user_id TEXT PRIMARY KEY,
                content TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
            ''')
            
            # 游戏状态表
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS game_state (
                id INTEGER PRIMARY KEY,
                phase TEXT,
                round INTEGER,
                remaining_time INTEGER,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            
            conn.commit()
        except Exception as e:
            logger.error(f"Failed to initialize database: {str(e)}")
            conn.rollback()
            raise
        finally:
            conn.close()
    
    def _get_connection(self) -> sqlite3.Connection:
        """获取数据库连接
        
        Returns:
            数据库连接对象
        """
        return sqlite3.connect(self.db_path)
    
    def execute(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """执行SQL查询
        
        Args:
            query: SQL查询语句
            params: 查询参数
            
        Returns:
            查询结果列表
        """
        conn = self._get_connection()
        try:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(query, params)
            
            if query.strip().upper().startswith(("SELECT", "PRAGMA")):
                rows = cursor.fetchall()
                result = [dict(row) for row in rows]
                return result
            else:
                conn.commit()
                return []
        except Exception as e:
            logger.error(f"Database error: {str(e)}")
            conn.rollback()
            raise
        finally:
            conn.close()
    
    def insert(self, table: str, data: Dict[str, Any]) -> int:
        """插入数据
        
        Args:
            table: 表名
            data: 数据字典
            
        Returns:
            插入记录的ID
        """
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?' for _ in data])
        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(query, tuple(data.values()))
            conn.commit()
            return cursor.lastrowid
        except Exception as e:
            logger.error(f"Database insert error: {str(e)}")
            conn.rollback()
            raise
        finally:
            conn.close()
    
    def update(self, table: str, data: Dict[str, Any], condition: str, params: tuple = ()) -> int:
        """更新数据
        
        Args:
            table: 表名
            data: 要更新的数据字典
            condition: WHERE条件
            params: 条件参数
            
        Returns:
            受影响的行数
        """
        set_clause = ', '.join([f"{k} = ?" for k in data.keys()])
        query = f"UPDATE {table} SET {set_clause} WHERE {condition}"
        
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(query, tuple(data.values()) + params)
            conn.commit()
            return cursor.rowcount
        except Exception as e:
            logger.error(f"Database update error: {str(e)}")
            conn.rollback()
            raise
        finally:
            conn.close()
    
    def delete(self, table: str, condition: str, params: tuple = ()) -> int:
        """删除数据
        
        Args:
            table: 表名
            condition: WHERE条件
            params: 条件参数
            
        Returns:
            受影响的行数
        """
        query = f"DELETE FROM {table} WHERE {condition}"
        
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor.rowcount
        except Exception as e:
            logger.error(f"Database delete error: {str(e)}")
            conn.rollback()
            raise
        finally:
            conn.close() 