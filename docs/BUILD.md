# 对应源码与构建记录

0.1.0 直接交付已验收的 fnos2 image/headers 和 mdadm，不为了改项目版本重新
编译内核。入口包单独以 0.1.0 打包。以下是现有构建路径，不保证逐字节复现。

## 固定输入

- Debian linux-source-7.2 `7.2.6-1~bpo13+1`。
- 源码 .deb SHA256：`e73de537b76ee6f17deedb149707ca7dec1a27499895bf2f6b51e782687dd0c6`。
- 解出的 linux-source-7.2.tar.xz SHA256：`48820cf63130e3b611127bc455009b365f1dbfae069612d812557ae5f1da0723`。
- 官方基线 config SHA256：`7a3ea73df2859e8705d874b24e199c5b5e2990314cf1e06b4b4380248a314663`。
- 最终 config SHA256：`6b7ffd510ffdda2ccc66cbeff8740fe028440d2553c991baa8525769cdc90e0c`。
- 内核 release：7.2.6-fnos2-amd64；包版本：7.2.6-1~fnos13+2。
- mdadm：官方 4.6-3 源码在 Debian 13 重建为 4.6-3~fnos13+1，只有 Debian
  changelog 改动，完整对应 Debian 源码包随发布交付。

## 内核

使用隔离 Debian 13 amd64 构建环境及普通构建用户。遵照随附 buildinfo 安装
对应编译依赖，编译器 x86_64-linux-gnu-gcc-14，使用原有 Rust/BTF 配套工具。
Rust 1.85.1、bindgen 0.71.1、LLVM/Clang 19 的确切 Debian 包与校验值另见
对应源码集合中的 rust-inputs.sha256；它补充 bindeb-pkg 生成的 buildinfo。
不要在生产系统混装整套其他发行版依赖。完整官方配置保留，不使用 localmodconfig。

解压精确源码并进入 linux-source-7.2，复制 config.debian 为 .config，执行：

```sh
scripts/config --enable MD_LLBITMAP --set-str LOCALVERSION '-fnos2-amd64'
scripts/config --set-str BUILD_SALT '7.2.6-fnos2-amd64'
make CC=x86_64-linux-gnu-gcc-14 olddefconfig
make CC=x86_64-linux-gnu-gcc-14 prepare
scripts/diffconfig ../config.debian .config
```

只接受随附 config.diff 的六项已审核差异：MD_LLBITMAP、LOCALVERSION、
BUILD_SALT、MODULE_SIG_ALL、MODULE_SIG_KEY、SYSTEM_TRUSTED_KEYS。
模块签名密钥由构建产生，不能包含在分发物中。官方基线省略的打包/签名配置
由完整配置过程补齐；这不代表获得 Debian 或 UEFI 信任。

在足够磁盘空间的临时目录中原生打包（并行数按资源选取）：

```sh
export LC_ALL=C.UTF-8
export DEBFULLNAME='fnOS support local test builder' DEBEMAIL=root@localhost
export DEB_RULES_REQUIRES_ROOT=no
export DPKG_DEB_COMPRESSOR_TYPE=zstd DPKG_DEB_COMPRESSOR_LEVEL=3
make -j2 CC=x86_64-linux-gnu-gcc-14 bindeb-pkg \
  KDEB_PKGVERSION='7.2.6-1~fnos13+2' \
  KDEB_CHANGELOG_DIST=trixie KDEB_SOURCENAME=linux-fnos
```

这次首次构建曾因构建资源限制中断，随后在同一隔离构建树恢复完成；
配置及产物经过审计，实际 image 包内有 4216 个模块。完整对应源码、最终配置、
生成的 Debian 打包说明和 buildinfo 应随发布保存。私钥、编译工作盘、调试包
和站点配置不分发。headers 另通过编译一个外部模块的 smoke test。

## mdadm

在另一个隔离工作目录使用随附 dsc 解包，dpkg-checkbuilddeps 通过后，以普通
用户运行 dpkg-buildpackage --build=full --no-sign。不运行可能破坏块设备的
上游 root 阵列测试套件。现有 4.6-3 比回移包更新，目标机不降级。

## 入口

```sh
sh tools/build-entry.sh "$PWD" /path/to/new-output-directory
```

入口只有 control、校验信息和文档，无 preinst/postinst/prerm/postrm。
打包不执行安装、格式化、磁盘发现或重启。最终发布需要再次做包级审计和
真实实验机安装/卸载测试；构建成功不等于通过发布门槛。
