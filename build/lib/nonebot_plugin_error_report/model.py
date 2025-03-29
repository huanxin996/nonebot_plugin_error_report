import json,os
from datetime import datetime
from typing import Optional, List, Dict, Any, Set
from pydantic import BaseModel
from nonebot.log import logger
from .config import error_config

class ErrorReportBase(BaseModel):
    id: int
    user_id: str
    bot_id: str
    session_id: str
    message: str
    error_type: str
    error_msg: str
    error_detail: Optional[str]
    plugin_name: str
    time: datetime

    class Config:
        json_encoders = {
            datetime: lambda v: v.strftime("%Y-%m-%d %H:%M:%S")
        }

if error_config.use_orm_database:
    from nonebot import require
    from tortoise import fields
    from tortoise.models import Model
    require("nonebot_plugin_tortoise_orm")
    from nonebot_plugin_tortoise_orm import add_model
    
    add_model("nonebot_plugin_error_report.model")
    
    class ErrorReport(Model):
        id = fields.IntField(pk=True)
        user_id = fields.CharField(max_length=64)
        bot_id = fields.CharField(max_length=64)
        session_id = fields.CharField(max_length=64)
        message = fields.TextField()
        error_type = fields.CharField(max_length=64)
        error_msg = fields.TextField()
        error_detail = fields.TextField(null=True)
        plugin_name = fields.CharField(max_length=64)
        time = fields.DatetimeField()

else:
    class JsonModel:
        _file_path: str
        _data: List[Dict[str, Any]] = []
        _counter: int = 0
        _fields: Dict[str, Any] = {}

        @classmethod
        def load_data(cls) -> None:
            if os.path.exists(cls._file_path):
                try:
                    with open(cls._file_path, "r", encoding="utf-8") as f:
                        cls._data = json.load(f)
                        if cls._data:
                            cls._counter = max(x.get("id", 0) for x in cls._data)
                except Exception as e:
                    logger.error(f"加载JSON文件失败: {e}")
                    cls._data = []

        @classmethod
        def save_data(cls) -> None:
            try:
                with open(cls._file_path, "w", encoding="utf-8") as f:
                    json.dump(cls._data, f, ensure_ascii=False, indent=2,
                            default=lambda x: x.strftime("%Y-%m-%d %H:%M:%S") if isinstance(x, datetime) else str(x))
            except Exception as e:
                logger.error(f"保存JSON文件失败: {e}")

    class ErrorReport(JsonModel):
        """错误报告模型"""
        _file_path = "error_reports.json"
        _fields = {
            "id": {"type": int, "primary_key": True},
            "user_id": {"type": str, "max_length": 64},
            "bot_id": {"type": str, "max_length": 64},
            "session_id": {"type": str, "max_length": 64},
            "message": {"type": str},
            "error_type": {"type": str, "max_length": 64},
            "error_msg": {"type": str},
            "error_detail": {"type": str, "null": True},
            "plugin_name": {"type": str, "max_length": 64},
            "time": {"type": datetime}
        }

        def __init__(self, **kwargs):
            for field, config in self._fields.items():
                if field in kwargs:
                    value = kwargs[field]
                    field_type = config["type"]
                    if field_type == datetime and isinstance(value, str):
                        try:
                            kwargs[field] = datetime.fromisoformat(value.replace(" ", "T"))
                        except ValueError:
                            kwargs[field] = datetime.now()
                    if field_type == str and "max_length" in config:
                        max_length = config["max_length"]
                        if len(str(value)) > max_length:
                            kwargs[field] = str(value)[:max_length]
            for k, v in kwargs.items():
                setattr(self, k, v)

        @classmethod
        async def create(cls, **kwargs) -> "ErrorReport":
            """创建新记录"""
            cls.load_data()
            cls._counter += 1
            if "time" not in kwargs:
                kwargs["time"] = datetime.now()
            if "id" not in kwargs:
                cls._counter += 1
                kwargs["id"] = cls._counter
            else:
                if kwargs["id"] > cls._counter:
                    cls._counter = kwargs["id"]
            error_dict = kwargs.copy()
            for field, config in cls._fields.items():
                if field not in error_dict and not config.get("null", False):
                    error_dict[field] = "" if config["type"] == str else None
            cls._data.append(error_dict)
            cls.save_data()
            return cls(**error_dict)

        @classmethod
        async def filter(cls, **kwargs) -> List["ErrorReport"]:
            """过滤查询"""
            cls.load_data()
            results = []
            for item in cls._data:
                match = True
                for k, v in kwargs.items():
                    if k.endswith("__lt"):
                        field = k[:-4]
                        if field == "time" and isinstance(v, str):
                            v = datetime.fromisoformat(v.replace(" ", "T"))
                        if not (field in item and item[field] < v):
                            match = False
                            break
                    elif k.endswith("__icontains"):
                        field = k[:-10]
                        if not (field in item and v.lower() in str(item[field]).lower()):
                            match = False
                            break
                    elif not (k in item and item[k] == v):
                        match = False
                        break
                if match:
                    results.append(cls(**item))
            return results

        @classmethod
        async def delete(cls, **kwargs) -> int:
            """删除符合条件的记录，返回删除的记录数"""
            cls.load_data()
            original_length = len(cls._data)
            deleted_ids = []
            new_data = []
            for item in cls._data:
                should_keep = True
                for k, v in kwargs.items():
                    if k.endswith("__lt"):
                        field = k[:-4]
                        if field == "time" and isinstance(v, str):
                            v = datetime.fromisoformat(v.replace(" ", "T"))
                        if field in item and item[field] < v:
                            should_keep = False
                            break
                    elif not (k in item and item[k] == v):
                        should_keep = False
                        break
                if should_keep:
                    new_data.append(item)
                else:
                    deleted_ids.append(item.get("id"))
            if len(new_data) != original_length:
                cls._data = new_data
                cls.save_data()
                logger.info(f"已删除 {original_length - len(new_data)} 条记录，ID: {deleted_ids}")

            return original_length - len(new_data)

        @classmethod
        async def all(cls) -> List["ErrorReport"]:
            """获取所有记录"""
            cls.load_data()
            return [cls(**item) for item in cls._data]

        @classmethod
        async def count(cls) -> int:
            """获取记录总数"""
            cls.load_data()
            return len(cls._data)

class ErrorCache:
    def __init__(self):
        self.unsent_errors: List[Dict] = []  # 未发送的错误记录
        self.sent_ids: Set[int] = set()      # 已发送的错误ID集合
        
    def add_error(self, error: Dict):
        """添加新的错误记录"""
        error_id = error["id"]
        if error_id not in self.sent_ids:
            self.unsent_errors.append(error)
    
    def mark_sent(self, error_ids: List[int]):
        """标记错误为已发送并清理"""
        self.sent_ids.update(error_ids)
        self.unsent_errors = [
            error for error in self.unsent_errors 
            if error["id"] not in self.sent_ids
        ]
        self.sent_ids.clear()
    
    def clear_sent(self):
        """清除所有已发送的错误记录"""
        self.unsent_errors.clear()
        self.sent_ids.clear()
    
    def get_unsent_errors(self) -> List[Dict]:
        """获取所有未发送的错误记录"""
        return self.unsent_errors
    
    def get_recent_errors(self, limit: int = 10) -> List[Dict]:
        """获取最近的n条错误记录"""
        return sorted(
            self.unsent_errors,
            key=lambda x: x.get('time', ''),
            reverse=True
        )[:limit]