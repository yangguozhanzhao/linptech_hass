# 基于Homeassistant结合领普设备的办公室控制系统

## 1.支持硬件

- 领普产品
  - [x] R3AC+天线，可以90m以上（910是50-60m）
  - [ ] 四路接收器+外置天线
  - [ ] K4R实现总控区域接收器，一个对多个接收器，距离品质稳定性有待提高
  - [ ] K5单开或G1S发射器，桌面一对一或者多对一控制一个接收器，基本没有问题
  - [ ] 中继器，中继控制命令（来自发射器或者控制中心）到接收器，中继状态值到控制中心
- 其他厂家
  - [x]小米温湿度，蓝牙

## 2. 安装配置说明

- 树莓派安装系统桌面版，`rpi-clone`
- [hass服务在树莓派上开机自启动](https://www.home-assistant.io/docs/autostart/systemd/)，systemd，注意路径为绝对路径
- chromium启动禁用双指缩放直接全屏 `/usr/bin/chromium-browser --kiosk --disable-pinch http://127.0.0.1:8123`,开机启动用`/home/pi/.config/autostart/my.desktop`

```sehll
[Desktop Entry]Type=Application
Exec = xhost +
Exec = chromium-browser --kiosk --disable-pinch http://127.0.0.1/
```

## 3. 软件开发

### 3.1 bug

- 开关控制时，控制中心会丢包（接收器状态返回），造成控制中心界面同步不及时
  - 开关是否应该加入到网络，收到开关信息时，查询对应的接收器
  - 总控由开关实现，关闭更加同步
- 总控是单独控制网内接收器，关闭不同步

### 3.2 待完善功能

- 四路接收器加入
- 开关加入

### 3.3 测试功能项

- 单独开关时，接收器受控制且有返回值
- 单独开关控制开关，界面同步
- 全开全关，所有接收器受控制且有返回值
- 开关全开全关，界面同步