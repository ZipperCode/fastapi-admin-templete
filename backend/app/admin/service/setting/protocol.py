from abc import ABC, abstractmethod
from typing import Dict

from app.admin.schemas.setting import SettingProtocolIn
from app.utils.config_util import ConfigUtil
from app.utils.common_util import ToolsUtil


class ISettingProtocolService(ABC):
    """政策协议服务抽象类"""

    @abstractmethod
    async def detail(self) -> Dict[str, dict]:
        pass

    @abstractmethod
    async def save(self, protocol_in: SettingProtocolIn):
        pass


class SettingProtocolService(ISettingProtocolService):
    """政策协议服务实现类"""

    async def detail(self) -> Dict[str, dict]:
        """获取政策协议信息"""
        default_val = '{"name":"","content":""}'
        service = await ConfigUtil.get_val('protocol', 'service', default_val)
        privacy = await ConfigUtil.get_val('protocol', 'privacy', default_val)
        return {
            'service': ToolsUtil.json_to_map(service),
            'privacy': ToolsUtil.json_to_map(privacy),
        }

    async def save(self, protocol_in: SettingProtocolIn):
        """保存政策协议信息"""
        await ConfigUtil.set('protocol', 'service', protocol_in.service.json(ensure_ascii=False))
        await ConfigUtil.set('protocol', 'privacy', protocol_in.privacy.json(ensure_ascii=False))

    @classmethod
    async def instance(cls):
        """实例化"""
        return cls()
