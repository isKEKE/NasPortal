# TODO LIST:
DASHBOARD需要完善

# 🧭 Alembic 常用命令大全（最常用操作）

| 命令                                       | 功能           | 说明                         |
|--------------------------------------------|----------------|------------------------------|
| `alembic init alembic`                      | 初始化         | 创建 Alembic 目录和配置       |
| `alembic revision -m "描述"`                 | 创建迁移脚本   | 手动编写迁移内容             |
| `alembic revision --autogenerate -m "描述"` | 自动生成迁移脚本 | 自动比对模型和数据库结构差异 |
| `alembic upgrade head`                       | 升级数据库     | 执行到最新迁移版本           |
| `alembic upgrade +1`                         | 升级一步       | 向上执行一步迁移             |
| `alembic downgrade -1`                       | 回滚一步       | 回退一条迁移                 |
| `alembic downgrade base`                     | 回滚全部       | 恢复到数据库初始状态         |
| `alembic current`                            | 当前版本       | 显示当前数据库的迁移版本     |
| `alembic history`                            | 历史版本       | 显示迁移历史                 |
| `alembic heads`                              | 所有最新分支   | 通常显示一个最新版本         |
| `alembic show <revision_id>`                 | 显示详情       | 查看指定迁移脚本的详细信息   |
| `alembic merge -m "merge branches" rev1 rev2` | 合并分支     | 多人协作时使用               |


---

# 📄 典型的 `alembic.ini` 配置文件示例

适用于 SQLite 或 PostgreSQL

```ini
# alembic.ini
[alembic]
script_location = alembic
sqlalchemy.url = sqlite:///./sql_app.db

# 替换为 PostgreSQL 示例：
# sqlalchemy.url = postgresql+psycopg2://user:password@localhost/dbname

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
