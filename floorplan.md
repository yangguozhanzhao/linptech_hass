# linptech Floorplan for Home Assistant

## 实现功能

- svg的导入导出
- 编辑模式和使用模式
- 设备状态个数根据 hass.states 变化
- 配置模式（chrome触屏,ipad等平板使用）
  - 领普设备位置拖动
  - 接触配对，发射器拖入到接收器的范围内1s后（图形显示），调用配对服务
  - 点按设备选中，并在右侧弹出关于该设备的信息和菜单（有些需要调用hass服务）
    - 开启和关闭中继
    - 闪烁
    - 隐藏设备
    - 删除设备
    - 删除配对
    - 其他
- 使用模式，只能点按设备，不能进行其他操作，也不会自动添加新的设备

## 数据格式

- `newHass.states`数据格式，每次收到信号就会更新
  - states为object，包含所有的实体
    - 每个实体都有唯一的`entity_id`
    - `state`存储开关，是否等，类型为字符（可以通过开关状态不同设备的颜色等不一样）
    - `attributes`存储其他属性值，如领普设备的id，type，channnel
  - 有group，light（接收器），switch（发射器），linptech.listen（是否为设置模式）四个类别的实体
  - 调用后台接口需要唯一的实体id，有些可能需要`attributes`中的设备属性值

```json
{
    group.all_lights: {entity_id: "group.all_lights", state: "on", attributes: {…}, …}
    group.all_switches: {entity_id: "group.all_switches",state: "off", attributes: {…}, …}
    light.8001734e: {entity_id: "light.8001734e",state: "on", attributes: {
        id: "8001734e", channel: "01", type: "81", friendly_name: "8001734e,rssi=25", supported_features: 0
        }, …}
    light.80017306: {entity_id: "light.80017306", state: "off", attributes: {…}, …}
    linptech.listen: {entity_id: "linptech.listen", state: "False", attributes: {…}, …}
    switch.000b0a99: {entity_id: "switch.000b0a99", state: "off", attributes: {
        id: "000b0a99", assumed_state: true, channel: "00", friendly_name: "000b0a99,rssi=42", type: "02"
        }, …}
    switch.000d7e9f: {entity_id: "switch.000d7e9f", state: "off", attributes: {…}, …}
}

```

- `floorplan.svg`svg文件，保存后会存储领普的设备信息
  - 保存设备在项目中的位置信息，设备信息（可能还有配对信息，暂时不考虑）
  - svg文件最后面有`transmitor_layer`和`transmitor_layer`两个g元素，下层子元素分别为发射器和接收器
  - 需要保存领普设备的一些信息在svg中，初始化的时候需要用到dev_id,dev_type,dev_channel等信息
  
    ```html
    <g id="transmitor_layer"></g>
    <g id="receiver_layer">
    <path 
        id="light.8001734e"
        dev_id="8001734e"
        dev_type="81"
        dev_channel="01"
        d="M512 85.333333C346.88 85.333333 213.333333 218.88 213.333333 384 213.333333 485.546667 264.106667 574.72 341.333333 628.906667L341.333333 725.333333C341.333333 748.8 360.533333 768 384 768L640 768C663.466667 768 682.666667 748.8 682.666667 725.333333L682.666667 628.906667C759.893333 574.72 810.666667 485.546667 810.666667 384 810.666667 218.88 677.12 85.333333 512 85.333333M384 896C384 919.466667 403.2 938.666667 426.666667 938.666667L597.333333 938.666667C620.8 938.666667 640 919.466667 640 896L640 853.333333 384 853.333333 384 896Z"
        class="draggable"
        transform="scale(0.012852297973632812),translate(0,1000)">
    </path>
    </g>
    ```
- `entityConfig`程序内部存储设备信息（一部分是读取SVG文件，一部分是后台通过states传过来的）
  - 代码中有