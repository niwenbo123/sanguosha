import pymysql

# 直接连接数据库添加字段
conn = pymysql.connect(
    host='localhost',
    user='root',
    password='niwenbo123',
    database='sanguo_assistant'
)

try:
    with conn.cursor() as cursor:
        cursor.execute("ALTER TABLE heroes ADD COLUMN tag VARCHAR(20) DEFAULT '标'")
    conn.commit()
    print("Column added successfully")
finally:
    conn.close()