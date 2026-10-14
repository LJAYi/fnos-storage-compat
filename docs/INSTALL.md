# 安装、升级、卸载与回退

本说明只适用已发布且校验通过的 0.1 离线集合。未通过发布验收的工作目录
不是稳定发行版。没有签名 APT 仓库或 Secure Boot 支持承诺。

## 前置条件

核对 OMV 8、Debian 13、amd64、BIOS；检查 /boot 和根分区空间。保存系统盘
及站点配置备份，并另外备份数据。确保数据盘唯一所有权、停止业务写入，
检查 OMV 是否有待应用配置。保留一个已经验证支持该布局的旧兼容内核。
不支持 llbitmap 的发行版旧内核不能算作数据盘可用的回退内核。

校验来源及 SHA256SUMS；哈希只能校验文件一致性，不能独立证明发布者身份。
先检查现有 mdadm：4.6-3 比 4.6-3~fnos13+1 新，不为统一版本而降级。

模拟安装明确文件，不使用 *.deb，不混入 debug、libc-dev 或任意发行版包：

```sh
sha256sum -c SHA256SUMS
dpkg-query -W base-files openmediavault mdadm
sudo apt-get -s --no-remove --no-install-recommends install \
  ./linux-image-7.2.6-fnos2-amd64_7.2.6-1~fnos13+2_amd64.deb \
  ./linux-headers-7.2.6-fnos2-amd64_7.2.6-1~fnos13+2_amd64.deb \
  ./omv-fnos-support_0.1.0_amd64.deb
```

若 mdadm 不满足依赖，再单独加入集合内确切回移包并重新模拟。审查无非预期
删除或升级后，去掉 -s 执行。不要运行 autoremove 或自动应用 OMV 配置。

检查 dpkg --audit、dpkg -V、initramfs 与真实 GRUB 菜单。选择新内核的步骤
因主机而异，不能复制他人的 root UUID 或菜单 ID。正常重启后必须确认
uname -r 为 7.2.6-fnos2-amd64，再核对 MD/LVM/ext4、llbitmap、权限、配额
和实际共享客户端。软件包安装不等于新内核已启用。

## 回退

停止业务写入，选择保留的旧兼容内核正常启动，核对数据及共享。
不要通过恢复 MD 头部、格式化或修改私有字段进行软件回退。
软件回退不能撤销磁盘数据写入；异常时保留证据与备份，不做清理。

## 卸载

先切换到保留的兼容内核并核实 uname -r，绝不移除正在运行的内核。
移除 omv-fnos-support 仅移除入口，不会自动删除依赖或数据。
要移除某个不用的 image/headers，先用 apt-get -s remove 对明确包名模拟，
检查没有连带删除 OMV、mdadm、LVM 等组件；再正常执行。不要自动降级 mdadm。
保留有用的旧包和配置直至确认恢复完成，不使用 purge 或 autoremove 批量清理。

已显式固定 GRUB 默认项的机器，安装、卸载和更新后均须审核默认项是否仍存在。
