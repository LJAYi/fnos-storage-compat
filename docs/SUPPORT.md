# 0.1 支持边界（冻结）

目标：OMV 8 / Debian 13 / amd64 / BIOS。实验系统 OMV 8.3.1-2。
不把基于 Debian 等同于已支持不含 OMV 的纯 Debian。

样本的飞牛版本为 1.2.0701（trim 包和 /usr/trim/etc/version 一致），
源内核 6.18.18.c1107-trim，trim-repo-release 1.2.3；版本文件自样本
初始化前未修改。记录来源版本不等于保证该版本创建的所有布局。

支持描述限于已测组合：

- GPT，128 GiB 可丢弃独立样本。
- 单成员 MD RAID1，metadata 1.2，512 字节逻辑扇区，llbitmap v6。
- 普通 PV/VG/线性 LV；不是 thin、cache 或加密卷。
- ext4，4 KiB block / 64 KiB cluster，含 bigalloc、metadata_csum、
  user/group/project quota 特征。
- 文件内容、数值 UID/GID、ACL、xattr、硬链接、软链接、稀疏和 Unicode。
- 原生 OMV 导入/启动恢复，NFSv4.2、SMB3.1.1 的已记录访问测试。

未验证：多盘 RAID、降级/重建/扩容、异常或未知私有字段、其他文件系统、
其他架构、UEFI/Secure Boot、其他发行版、硬件断电及写后返回飞牛。
实验虚拟机强制停止仅模拟客体掉电，不等于真实控制器/磁盘断电认证。

已知操作边界：

1. 该 mdadm 组装路径需要可写打开成员，不能承诺硬件只读成员可组装。
   保护原样本，用独立副本测试；MD readonly 与 ext4 ro,noload 不等于硬件只读。
2. mdadm --examine-bitmap 对 v6 的显示有限，不能单凭其未知版本报文判断损坏；
   运行时必须核验 sysfs bitmap_type 的 [llbitmap]。
3. 配额必须由 OMV 配置并验证 EDQUOT；不能只看 ext4 配额特征。
4. 传统 quotaon@ 单元可能重复启用 ext4 内置配额；仅对确认为重复的单卷实例
   处理，绝不全局屏蔽。此站点配置不属于包的自动行为。
5. 旧手工内核可能在 GRUB 排序中位于新内核之前；安装完成后必须核验真实启动项。

0.1.x 仅修复上述支持范围内的缺陷、安全问题、构建/文档错误。
新增平台或存储布局必须另开版本并重新定义测试矩阵，不隐式扩大 0.1 支持承诺。
