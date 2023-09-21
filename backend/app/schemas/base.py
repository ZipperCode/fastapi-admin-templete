from datetime import datetime
from typing import TypeVar, Generic, Sequence, Union, Annotated

from fastapi import Query
from fastapi_pagination.bases import AbstractParams, RawParams, AbstractPage
from pydantic import BaseModel, WrapSerializer, PlainSerializer

T = TypeVar("T")
C = TypeVar("C")

DATE_TIME_FMT = "%Y-%m-%d %H:%M:%S"

DateTime = Annotated[
    datetime,  PlainSerializer(lambda dt: dt.strftime(DATE_TIME_FMT), return_type=str, when_used='json')
]

class PageParams(BaseModel, AbstractParams):
    pageNo: int = Query(1, ge=1, description='Page Number')
    pageSize: int = Query(20, gt=0, le=60, description='Page Size')

    def to_raw_params(self) -> RawParams:
        offset = (self.pageNo - 1) * self.pageSize
        return RawParams(limit=self.pageSize, offset=offset)


class Page(AbstractPage[T], Generic[T]):
    """
    分页结果封装
        items: 返回集列表
        total: 结果总数
    """
    count: int
    pageNo: int
    pageSize: int
    lists: Sequence[T]

    __params_type__ = PageParams

    @classmethod
    def create(cls, items: Sequence[T], total: int, params: PageParams):
        return cls(lists=items, count=total, pageNo=params.pageNo, pageSize=params.pageSize)


def empty_to_none(v: str) -> Union[str, None]:
    """替换空字符为None"""
    if v == '':
        return None
    return v
