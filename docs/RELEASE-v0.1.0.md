# fnOS Storage Compat 0.1.0

社区首版：只整理并发布已有能力，不新增功能或兼容性。0.1.x 仅修复缺陷。
非飞牛或 OpenMediaVault 官方项目。

## 支持范围

OMV 8 / Debian 13 / amd64 / BIOS；已测 fnOS 1.2.0701 创建的单成员 Basic：
MD RAID1 metadata 1.2 / llbitmap → 普通线性 LVM → ext4。
不承诺其他布局、发行版、架构、UEFI/Secure Boot 或写入后重新交回飞牛。
Basic 单成员没有冗余。需要系统和数据备份，且磁盘必须只有一个读写所有者。

## 下载

- `fnos-storage-compat-v0.1.0-omv8-debian13-amd64.tar`：四个 .deb、包校验清单、
  安装/回退/兼容范围/测试文档、构建脚本和配置。
- `fnos-storage-compat-v0.1.0-corresponding-source.tar`：精确 Linux 源码、
  mdadm Debian 源码包、构建配置及构建记录。**这不是 GitHub 自动生成的项目源码包。**
- `SHA256SUMS`：以上两个归档的 SHA256。校验保证文件一致性，不是独立数字签名。

Linux 用户在下载目录执行 `sha256sum -c SHA256SUMS`；然后解开离线包，
按 `docs/INSTALL.md` 先模拟安装。不要通配安装所有 .deb，不运行 autoremove。
如果现有 mdadm 为 4.6-3，不要降级到附带的 4.6-3~fnos13+1。

## 软件组成

- image/headers：7.2.6-fnos2-amd64 / 7.2.6-1~fnos13+2，复用已经验收的二进制。
- 可选 mdadm：4.6-3~fnos13+1。
- 入口：omv-fnos-support 0.1.0，无维护脚本或后台服务。

没有自动格式化、转换、导入、共享、改权限或重启功能；标准内核/mdadm 安装
钩子仍会更新 initramfs/GRUB 或触发设备发现，需要维护窗口。

## 验收

干净安装、旧系统副本迁移、真实升级/回退、卸载重装、权限/配额、原生 OMV
自动挂载和限定协议访问测试通过。另通过 15 分钟持续读写（420轮，约7.05GB）
及一次可丢弃 VM 的负载中强制停止/恢复；40个已确认文件哈希和卸载后的只读
文件系统检查通过。详细观察与边界见 docs/TESTING.md。

这是限定范围的实验验收，不是对所有硬件或真实物理掉电的认证；没有升级任何
生产实例。正常读写会改变日志/元数据；软件回退不能撤销写入。

源码与第三方许可随发行提供；没有签名 APT 仓库、Secure Boot 承诺或自动更新服务。
