# 构建矩阵

核心目标为 Yocto 6.0.4 Wrynose。源码确定、配置确定、实际编译与目标启动分别记录。

| 产品入口 | 源码与配置状态 | MACHINE | 编译 / 启动状态 |
| --- | --- | --- | --- |
| products/qemuarm64/default.xml | 核心官方发布提交，OE-Core 默认配置 | qemuarm64 | 尚未完整编译 / 启动验收 |
| products/kickpi-k7/integration.xml | Wrynose 核心与 Rockchip；K7 layer 仍为 Scarthgap，迁移阻塞 | kickpi-k7 | 不可宣称兼容 Wrynose |
| products/rk3576-evb/integration.xml | 有上游 machine，产品发行版与 image 未选定 | rockchip-rk3576-evb | 待构建及实机验收 |
| products/stm32mp157-demo/integration.xml | ST Wrynose BSP，具体 MP157 板型与发行版未选定 | 待确认 | 未验证 |
| products/zynq7020-demo/integration.xml | Xilinx Wrynose BSP，板型与工具流程未选定 | 待确认 | 未验证 |

根 default 和 products/kickpi-k7/default.xml 是 K7 候选入口别名，状态相同。

## Layer 配置要求

- QEMU：OE-Core 默认模板启用 sources/openembedded-core/meta；选 Poky distro 时另启用 sources/meta-yocto/meta-poky。
- Rockchip：核对 core、meta-openembedded/meta-oe、meta-rockchip。
- K7：还需 meta-kickpi；移植兼容声明、配方追加、设备树并验证，不能只放宽 LAYERSERIES_COMPAT。
- STM32：核对 core、meta-oe、meta-python、ST BSP 及所选发行版实际依赖。
- Xilinx：核对 core、meta-arm/meta-arm-toolchain、meta-arm/meta-arm、meta-xilinx/meta-xilinx-core，再按板型及 SDT/XSCT 流程选择其它 layer、工具和硬件输入。仓库根目录并非统一的 layer 根目录。

所选 Xilinx Wrynose 提交没有 gitlink。其 README.building.md 将 gen-machine-conf 列为独立仓库（分支 xlnx_rel_v2026.1-wrynose），不能把旧 Scarthgap 的子模块结构套用到新版。
本清单尚未决定使用生成 machine 的流程，因此没有默认添加该工具；需要时再加入真实仓库和固定提交。
来源：[所选提交的构建说明](https://git.yoctoproject.org/meta-xilinx/tree/README.building.md?id=1231e93e0aa083d67ad60e9670733addcc501e92)。

MACHINE、DISTRO、IMAGE、BBLAYERS 将由真实 yocto-platform 的 profile 和模板控制，不从 XML 文件名推导。

## 发布条件

1. 空目录同步并核对各 project HEAD 与 XML SHA。
2. 确认 layer 系列、依赖、MACHINE、发行版与 image，完成 BitBake 解析。
3. 固定实际启用的动态 SRCREV，完成镜像和 SDK 构建。
4. 实机或 QEMU 验证，保存测试、版本及构建环境记录。
5. 满足上述条件才添加产品 release；当前不创建虚构的 1.0.0 发布。

