# linptech API文档

> - 树莓派+home assistant 0.77
> - linptech 0.1.7
> - 杨展 20190110

## API接口

### 接口权限

- 所有API的请求header带 `X-HA-Access: YOUR_PASSWORD` 默认密码87413985
- 接口地址：`http://IP_ADDRESS/api/`

### GET /api/

- 查看API，正常返回

```json
{
  "message": "API running."
}
```

### GET /api/states

- 获取所有实体
- entity_id以light开头为linptech的接收器，其余可以不管
- state为当前开关的状态

```json
[
    {
        "attributes": {
            "friendly_name": "r6,rssi=54",
            "supported_features": 0
        },
        "context": {
            "id": "fa2b71b1d5774dbe8b24cd6fe08aeacb",
            "user_id": null
        },
        "entity_id": "light.r6",
        "last_changed": "2019-01-10T08:43:37.890178+00:00",
        "last_updated": "2019-01-10T08:43:37.890178+00:00",
        "state": "on"
    },
        {
        "attributes": {
            "friendly_name": "2,rssi=59",
            "supported_features": 0
        },
        "context": {
            "id": "d782224c934f4f25981afc039eb70ce7",
            "user_id": null
        },
        "entity_id": "light.2",
        "last_changed": "2019-01-10T08:43:39.231992+00:00",
        "last_updated": "2019-01-10T08:43:39.600825+00:00",
        "state": "on"
    }
    ...
]
```

### GET /api/states/<entity_id>

- 获取指定实体的状态，结构同上

### POST /api/services/light/turn_on

- 打开灯，例如关闭entity_id = "light.r6"
- 发送数据，必须json格式，如没有数据则会打开所有灯

```json
{
    "entity_id": "light.r6"
}
```

- 返回数据

```json
[
    {
        "attributes": {
            "friendly_name": "r6,rssi=49",
            "supported_features": 0
        },
        "context": {
            "id": "b4c164912b25484288b2eff32db58db9",
            "user_id": null
        },
        "entity_id": "light.r6",
        "last_changed": "2019-01-10T09:04:25.268799+00:00",
        "last_updated": "2019-01-10T09:04:25.268799+00:00",
        "state": "on"
    }
]
```

### POST /api/services/light/turn_off

- 关闭灯，使用方式同上