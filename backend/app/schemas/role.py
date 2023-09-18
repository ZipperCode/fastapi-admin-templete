import datetime
from typing import Union, List, Optional

from fastapi import Query
from pydantic import BaseModel, Field

from app.schemas.base import PageParams


class SystemRoleCreateIn(BaseModel):
    """新增角色参数"""
    name: str = Field(min_length=1, max_length=30)  # 角色名称
    sort: int = Field(ge=0)  # 角色排序
    is_disable: int = Field(alias='isDisable', ge=0, le=1)  # 是否禁用: [0=否, 1=是]
    remark: str = Field(default='', max_length=200)  # 角色备注
    menu_ids: Union[str, None] = Field(alias='menuIds')  # 关联菜单


class SystemRoleEditIn(SystemRoleCreateIn):
    """编辑角色参数"""
    id: int = Field(gt=0)  # 主键


class SystemRoleDelIn(BaseModel):
    """删除角色参数"""
    id: int = Field(gt=0)  # 主键


class SystemRoleOut(BaseModel):
    """系统角色返回信息"""
    id: int  # 主键
    name: str  # 角色名称
    createTime: datetime = Field(alias='create_time')  # 创建时间
    updateTime: datetime = Field(alias='update_time')  # 更新时间

    class Config:
        from_attributes = True


class SystemRoleDetailIn(BaseModel):
    id: int = Field(gt=0)  # 主键

class SystemRoleDetailOut(SystemRoleOut):
    """系统角色返回信息"""
    remark: str  # 角色备注
    menus: List[int] = Field(default_factory=list)  # 关联菜单
    member: int = Field(default=0)  # 成员数量
    sort: int  # 角色排序
    isDisable: int = Field(alias='is_disable')  # 是否禁用: [0=否, 1=是]

    class Config:
        from_attributes = True


class SystemRoleListIn(PageParams):
    """角色列表查询参数"""
    keyword: Optional[str] = Query()
