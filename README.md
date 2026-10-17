# fnOS Storage Compat

**为 OpenMediaVault 提供飞牛 Basic 数据盘的原生读写兼容支持。**

fnOS Storage Compat 将经过验证的 Linux 内核、mdadm 与依赖组合打包为 `.deb`，
帮助 OMV 通过原生 MD、LVM 和 ext4 接管受支持的飞牛数据盘，无需手工转换磁盘格式。
共享、用户和权限继续由 OMV 管理。

[下载 v0.1.0](https://github.com/LJAYi/fnos-storage-compat/releases/tag/v0.1.0) ·
[安装指南](docs/INSTALL.md) ·
[兼容范围](docs/SUPPORT.md) ·
[问题反馈](https://github.com/LJAYi/fnos-storage-compat/issues)

> 社区项目，非飞牛或 OpenMediaVault 官方项目。当前仅支持下述已验证组合，
> 不是通用磁盘转换或数据恢复工具。操作前请备份系统和数据。

## 项目提供什么

- **原生存储支持**：提供启用 `llbitmap` 支持的内核及配套工具，沿用 Linux 存储栈。
- **标准 Debian 软件包**：通过 `omv-fnos-support` 入口包声明经过验证的组件依赖，使用 APT 安装和管理。
- **可核验的交付**：提供离线安装包、SHA256 校验清单、对应源码、构建说明及测试报告。
- **明确的维护边界**：提供升级、卸载和回退指南；`0.1.x` 仅修复缺陷，不扩大兼容范围。

项目不自动格式化、转换、迁移、修复或导入磁盘，也不替代 OMV 的 NFS/SMB 和账户管理。

## 支持范围

| 项目 | v0.1 已验证范围 |
| --- | --- |
| 目标系统 | OpenMediaVault 8 / Debian 13 |
| 架构与启动方式 | amd64 / BIOS |
| 飞牛样本版本 | fnOS 1.2.0701 |
| 存储布局 | Basic：GPT → 单成员 MD RAID1（metadata 1.2 / llbitmap）→ 普通线性 LVM → ext4 |
| 验证样本 | 128 GiB 独立测试盘；详细文件系统特征见兼容文档 |

**不承诺支持**其他发行版或架构、UEFI/Secure Boot、多盘 RAID、阵列重建与扩容、
其他文件系统，以及未知或损坏的磁盘布局。飞牛版本相同，也不代表其所有存储布局都受支持。

已完成限定范围的安装、升级、回退、卸载重装、持续读写和样本模拟掉电恢复测试。
这些结果不是对所有硬件或真实物理掉电的认证，详见 [兼容边界](docs/SUPPORT.md) 和 [测试报告](docs/TESTING.md)。

## 开始使用

1. 阅读 [兼容范围](docs/SUPPORT.md)，确认系统和磁盘布局符合要求，并完成备份。
2. 在 [v0.1.0 发行页](https://github.com/LJAYi/fnos-storage-compat/releases/tag/v0.1.0) 下载
   `fnos-storage-compat-v0.1.0-omv8-debian13-amd64.tar` 和 `SHA256SUMS`，按清单核对归档的 SHA256。
3. 解压离线包，按照 [安装指南](docs/INSTALL.md) 检查依赖并模拟安装，确认后在维护窗口执行。
4. 正常重启并核验实际运行的内核，再检查磁盘、权限、配额和共享访问。

不要使用 `*.deb` 通配安装所有包，也不要为统一版本而降级现有 mdadm。
当前通过 GitHub Releases 提供离线包，**尚无签名 APT 软件源或自动更新服务**。

### 使用前须知

- **同一块磁盘只能有一个读写所有者**，不得由飞牛和 OMV 同时读写。
- Basic 单成员不提供冗余；正常读写会修改文件系统、MD 元数据和日志，不是“零改动”访问。
- 不保证写入后能直接将磁盘交回飞牛；软件回退不能撤销数据写入。
- 入口包不含维护脚本，但内核和 mdadm 的标准安装钩子仍可能更新 initramfs/GRUB 或触发设备发现。
- 保留已验证的兼容内核和备份；普通旧内核不一定能作为可用的存储回退环境。

## 软件组成

| 组件 | 用途 |
| --- | --- |
| `omv-fnos-support` | 声明 OMV 8 与已验证组件版本的入口依赖包 |
| Linux image / headers | `7.2.6-fnos2-amd64` 内核及配套头文件 |
| mdadm | 提供 `4.6-3~fnos13+1` 回移包，仅在现有版本不满足依赖时使用；不降级现有 `4.6-3` |
| 源码与构建材料 | 对应源码、配置、构建记录、校验清单和文档 |

需要源码时，请下载发行页中的 `fnos-storage-compat-v0.1.0-corresponding-source.tar`。
GitHub 自动生成的 **Source code** 压缩包只包含本仓库，不能替代内核和 mdadm 的对应源码归档。

## 文档

- [安装、升级、卸载与回退](docs/INSTALL.md)
- [兼容范围与已知限制](docs/SUPPORT.md)
- [测试方法与验收结果](docs/TESTING.md)
- [对应源码与构建说明](docs/BUILD.md)
- [发布与维护政策](docs/RELEASING.md)
- [更新日志](CHANGELOG.md)

## 反馈与贡献

欢迎通过 [GitHub Issues](https://github.com/LJAYi/fnos-storage-compat/issues) 报告可复现问题，
或提交文档、构建和缺陷修复。请提供系统与软件包版本、实际内核版本、存储布局、复现步骤和脱敏日志。
不要公开凭据、私钥、完整 OMV 配置或用户数据。

`0.1.x` 聚焦当前支持范围内的缺陷、安全、构建和文档修复。
新增平台或存储布局需要独立测试和后续版本规划，不以“编译成功”作为兼容性承诺。

## 许可证

本项目新增脚本与文档采用 [MIT License](LICENSE)。Linux 内核、mdadm 和 Debian
相关材料保留各自许可证，详见 [版权与对应源码说明](COPYRIGHT.md)。
