# entari-plugin-user

![python](https://img.shields.io/badge/python-3.10+-blue.svg?style=flat-square)
![pypi](https://img.shields.io/pypi/v/entari-plugin-user.svg?style=flat-square)

Entari 用户系统插件，用于统一管理用户信息、跨平台账号绑定和权限等级控制。

## 安装

```bash
pip install entari-plugin-user
# or use pdm
pdm add entari-plugin-user
# or use uv
uv add entari-plugin-user
```

## 配置

| 配置项 | 必填 | 默认值 |
| :---: | :---: | :---: |
| user_token_prefix | 否 | entari/ |

## 使用

### 查看用户信息

```bash
/user
```

### 改名

```bash
/user -n <username>
/callme <username>
```

### 绑定

```bash
/bind [-r|--revoke]
```

### 授权

> [!NOTE]
> 本项目的权限管理了参考 [Koishi](https://koishi.chat/zh-CN/manual/usage/customize.html#%E6%9D%83%E9%99%90%E7%AE%A1%E7%90%86) 的方案  
> 我们也推荐开发者按照其标准进行管理  
>
> - 0 级：黑名单用户，机器人不会响应其指令
> - 1 级：所有用户，只能够接触有限的功能  
> - 2 级：高级用户，能够接触几乎一切机器人的功能  
> - 3 级：管理员，能够直接操作机器人事务  
> - 4 级：高级管理员，能够管理其他账号  
> - 5 级：超级管理员（SUPERUSER）  

```bash
/auth <level> -u <@用户>
```

```bash
/auth --superuser [token]
```

## 插件适配

### 获取用户信息

```py
from arclet.entari import command
from entari_plugin_user import User, UserSession  # entari:plugin

@command.on("me")
async def _(session: UserSession):
    await session.send(f"You're {session.user_name}({session.platform_id})")
```

### 权限过滤

```py
from arclet.entari import command, propagate
from entari_plugin_user import Authorization, only_superuser  # entari:plugin

@command.on("ban")
@propagate(Authorization(3))
async def _ban():
    ...

@command.on("sudo")
@only_superuser
async def _sudo():
    ...
```

## 鸣谢

- [`koishijs/koishi`](https://github.com/koishijs/koishi): 提供权限管理规范
- [`he0119/nonebot-plugin-user`](https://github.com/he0119/nonebot-plugin-user)：本项目直接参考
