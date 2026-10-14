# 版权和对应源码

本仓库新增的脚本及文档采用 MIT（见 LICENSE）。第三方内容不因放入本项目而
改用 MIT：Linux 内核按自身 COPYING、LICENSES 和各源文件许可证分发；mdadm
及其 Debian 包装按对应源码的 COPYING/debian/copyright 分发；Debian 内核配置
保留上游来源和许可证。具体声明以交付的对应源码为准。

二进制发布必须同时提供精确内核源码归档、最终配置、构建说明、构建版本记录，
以及 mdadm 对应 .dsc/.orig.tar.xz/.debian.tar.xz。不能只提供一个未来可能失效
的下载链接，也不能只发布 .deb 而省略对应源码。

不分发用于构建时模块签名的私钥。APT 签名、内核模块签名和 UEFI Secure Boot
信任是不同机制；0.1 不承诺 Secure Boot。构建输入可核验，不宣称目前已实现
逐字节可复现构建。
