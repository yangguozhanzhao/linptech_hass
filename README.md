# linptech设备与Homeassistant

## 期望实现的功能

- linptech的设备可以加入到homeassistant中，通过领普串口模块能够实现基本操控（打开/关闭/配对/清除/读取状态/设置）
- 可以利用homeassistant的floorplan（平面图）+ HADashboard 行进展示并操控
  - 多层是可以实现的
- ![fllorplan](https://ws2.sinaimg.cn/large/006tNbRwgy1fuevpyydx6j30dj0ehq3f.jpg)
- ![HADashboard](https://ws1.sinaimg.cn/large/006tNbRwgy1fuevq8farlj30s30kptas.jpg)

## tips

- 一般位于 `~/.homeassistant/` ,可以修改到项目文件下 `hass --config path/to/config`,用自己配置文件运行web页面`hass --config config_path --open-ui`
- 测试配置文件的有效性 `hass --script check_config`
- YAML文件规则
  - 在“#”右边的文字用于注释，不起实际作用。
  - 冒号（:）左边的字符串代表配置项的名称，冒号右边是配置项的值。
  - 如果冒号右边是空的，那么下一行开始所有比这行缩进（左边多两个空格）的都是这个配置项的值。
  - 如果配置项的值以减号（-）开始，代表这个配置项有若干个并列的值（也可能仅并列一个），每个都是以相同缩进的减号开始。
