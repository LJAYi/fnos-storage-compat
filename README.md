# fnOS Storage Compat

面向 **OMV 8 / Debian 13 / amd64 / BIOS** 的飞牛 Basic 存储兼容支持包。
社区项目，非飞牛或 OpenMediaVault 官方项目。

## 0.1.0 范围

使用原生 Linux MD、LVM 和 ext4 访问已初始化的受支持磁盘，不要求手工转换
磁盘格式。0.1.0 只整理已有能力；不新增平台、存储布局或后台服务。

已测样本来源：fnOS `1.2.0701`，源内核 `6.18.18.c1107-trim`，128 GiB
独立 Basic + ext4。结构为 GPT → 单成员 MD RAID1 / metadata 1.2 /
llbitmap → 普通线性 LVM → ext4。Basic 单成员不提供冗余。

**0.1.0：已通过本文限定范围的实验验收。**
安装、升级、回退、卸载重装、持续读写和样本模拟掉电恢复均已通过；
范围和证据见 [测试记录](docs/TESTING.md)。

下载：[v0.1.0 Release](https://github.com/LJAYi/fnos-storage-compat/releases/tag/v0.1.0)。
选择 `fnos-storage-compat-v0.1.0-omv8-debian13-amd64.tar` 离线包，先按 Release
的 `SHA256SUMS` 校验归档，再解包并阅读 `docs/INSTALL.md`。对应第三方源码另附
`fnos-storage-compat-v0.1.0-corresponding-source.tar`；GitHub 自动生成的 Source code
压缩包只有本项目代码，不能替代这个对应源码归档。

## 交付

- `omv-fnos-support`：稳定名称的入口依赖包，0.1.0 仍明确依赖 OMV 8。
- `linux-image-7.2.6-fnos2-amd64` 和配套 headers：版本 `7.2.6-1~fnos13+2`。
- `mdadm 4.6-3~fnos13+1`：仅当现有工具不满足依赖时使用；不得降级现有 4.6-3。
- 对应源码、配置、构建说明、校验清单与测试报告。

不实现 NFS/SMB、账户管理、数据迁移、自动导入或修复。共享和权限由 OMV
管理。入口包不包含维护脚本；内核和 mdadm 的标准安装钩子仍可能更新
initramfs/GRUB 和触发设备发现，必须在维护窗口安装。

阅读 [兼容边界](docs/SUPPORT.md)、[安装和回退](docs/INSTALL.md)、
[源码与构建](docs/BUILD.md)、[更新政策](docs/RELEASING.md)。

正常读写会更新磁盘元数据和日志；软件回退不能撤销数据写入。
不保证写入后能直接交回飞牛。使用前备份数据，并确保磁盘只有一个读写所有者。

项目新增脚本和文档采用 MIT；内核、mdadm、Debian 配置等第三方内容保留
各自许可证，详见 [版权说明](COPYRIGHT.md)。
