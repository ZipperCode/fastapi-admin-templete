from datetime import datetime
from typing import Literal, Union, List, Optional

from fastapi import Query
from pydantic import BaseModel, Field

from app.schemas.base import PageParams


class SystemMenuCreateIn(BaseModel):
    """新增菜单参数"""
    pid: int = Field(ge=0)  # 上级菜单
    menu_type: Literal['D', 'M', 'B'] = Field(alias='menuType')  # 权限类型: [D=目录, M=菜单, B=按钮]
    menu_name: str = Field(alias='menuName', min_length=1, max_length=30)  # 菜单名称
    menu_icon: Union[str, None] = Field(alias='menuIcon', max_length=100)  # 菜单图标
    menu_sort: int = Field(alias='menuSort', ge=0)  # 菜单排序
    perms: Union[str, None] = Field(max_length=100)  # 权限标识
    paths: Union[str, None] = Field(max_length=200)  # 路由地址
    component: Union[str, None] = Field(max_length=200)  # 前端组件
    selected: Union[str, None] = Field(max_length=200)  # 选中路径
    params: Union[str, None] = Field(max_length=200)  # 路由参数
    is_cache: int = Field(alias='isCache', ge=0, le=1)  # 是否缓存: [0=否, 1=是]
    is_show: int = Field(alias='isShow', ge=0, le=1)  # 是否显示: [0=否, 1=是]
    is_disable: int = Field(alias='isDisable', ge=0, le=1)  # 是否禁用: [0=否, 1=是]


class SystemMenuDelIn(BaseModel):
    """删除菜单参数"""
    id: int = Field(gt=0)  # 主键


class SystemMenuEditIn(SystemMenuCreateIn):
    """编辑菜单参数"""
    id: int = Field(gt=0)  # 主键


class SystemMenuDetailIn(BaseModel):
    """菜单详情参数"""
    id: int = Query(gt=0)  # 主键


class SystemMenuListIn(PageParams):
    """菜单列表查询参数"""
    keyword: Optional[str] = Query()


class SystemMenuOut(BaseModel):
    """系统菜单返回信息"""
    id: int  # 主键
    pid: int  # 上级菜单
    menuType: str = Field(alias='menu_type')  # 权限类型: [M=目录, C=菜单, A=按钮]
    menuName: str = Field(alias='menu_name')  # 菜单名称
    menuIcon: str = Field(alias='menu_icon')  # 菜单图标
    menuSort: int = Field(alias='menu_sort')  # 菜单排序
    perms: str  # 权限标识
    paths: str  # 路由地址
    component: str  # 前端组件
    selected: str  # 选中路径
    params: str  # 路由参数
    isCache: int = Field(alias='is_cache')  # 是否缓存: [0=否, 1=是]
    isShow: int = Field(alias='is_show')  # 是否显示: [0=否, 1=是]
    isDisable: int = Field(alias='is_disable')  # 是否禁用: [0=否, 1=是]
    createTime: datetime = Field(alias='create_time')  # 创建时间
    updateTime: datetime = Field(alias='update_time')  # 更新时间

    class Config:
        from_attributes = True


class MenuOut(SystemMenuOut):
    children: Union[List['SystemMenuOut'], None]  # 子集

    class Config:
        from_attributes = True
