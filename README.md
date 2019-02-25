# 基于Homeassistant结合领普设备的办公室控制系统

## 1.支持硬件

- 领普产品
  - [x] 接收器：R3AC+四路接收器
  - [x] K4R实现总控区域接收器，一个对多个接收器，距离品质稳定性有待提高
  - [x] K5单开或G1S发射器，桌面一对一或者多对一控制一个接收器，基本没有问题

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
- 配置后重启进行测试
  - 单独点按界面时，接收器受控制且有返回值
  - 单独开关控制开关，界面同步
  - 界面全开全关，所有接收器受控制且有返回值
  - 开关全开全关，界面同步

## 3. 软件开发

### 3.1 bug

- 开关控制时，控制中心会丢包（接收器状态返回），造成控制中心界面同步不及时
  - 开关是否应该加入到网络，收到开关信息时，查询对应的接收器
  - 总控由开关实现，关闭更加同步
- 总控是单独控制网内接收器，关闭不同步

### 3.2 待完善功能

- 开关加入
- 自定义配置界面开发

<svg xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:cc="http://creativecommons.org/ns#" xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns:svg="http://www.w3.org/2000/svg" xmlns="http://www.w3.org/2000/svg" xmlns:sodipodi="http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd" xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape" viewBox="0 0 362.20996 257.04596" version="1.1" xml:space="preserve" id="svg475" sodipodi:docname="21-Model.svg" width="362.20996" height="257.04596" style="fill-rule: evenodd; stroke-linecap: round; stroke-linejoin: round; height: 100%; width: 100%; position: absolute;" inkscape:version="0.92.3 (2405546, 2018-03-11)">

<svg id="SvgjsSvg1001" width="100%" height="100%" xmlns="http://www.w3.org/2000/svg" version="1.1" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:svgjs="http://svgjs.com/svgjs">