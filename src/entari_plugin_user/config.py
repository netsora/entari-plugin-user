from arclet.entari import BasicConfModel, plugin


class Config(BasicConfModel):
    user_token_prefix: str = "entari/"
    """生成令牌的前缀"""


config = plugin.get_config(Config)
