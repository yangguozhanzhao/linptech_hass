# 基于Homeassistant结合领普设备的办公室控制系统

> 定位于单层办公楼，集成灯控+空调+视频+IT设备

## 1. 支持硬件

- 手动配置，不自动发现
- 灯控
- 空调
- 视频
- IT设备

## 2. 安装配置说明

- 树莓派安装系统桌面版，`rpi-clone`
- [hass服务在树莓派上开机自启动](https://www.home-assistant.io/docs/autostart/systemd/)，systemd，注意路径为绝对路径,user默认为root，不要设置
- chromium启动禁用双指缩放直接全屏(没有直接连接触屏可以不配置) `/usr/bin/chromium-browser --kiosk --disable-pinch http://127.0.0.1`,开机启动用`/home/pi/.config/autostart/my.desktop`

```sehll
[Desktop Entry]Type=Application
Exec = xhost +
Exec = chromium-browser --kiosk --disable-pinch http://127.0.0.1/
```

- linptech_debug导出linptech.yaml,替换即可
- 路由器设置：
  - 绑定ip和mac地址，
  - 如果支持自定义host，可以将ip和域名`linptech.net`,实现域名访问