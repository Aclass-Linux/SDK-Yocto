# Manifest 目录架构

参考 NXP 的 sources/ 和构建入口组织、ST 的 BSP/发行版/脚本分工，以及 Toradex 的产品和集成入口划分。目录名称是本项目约定。
来源：[NXP Wrynose manifest](https://github.com/nxp-imx/imx-manifest/blob/imx-linux-wrynose/imx-6.18.20-2.0.0.xml)、[ST manifest](https://github.com/STMicroelectronics/oe-manifest/blob/scarthgap/default.xml)、[Toradex 工程说明](https://developer.toradex.com/linux-bsp/os-development/reference-documentation/)。

## 组合规则

```text
default.xml
└── products/kickpi-k7/default.xml
    └── products/kickpi-k7/integration.xml
        ├── remotes.xml
        ├── base/yocto.xml
        ├── base/openembedded.xml
        ├── base/project.xml
        └── boards/kickpi-k7.xml
            ├── bsp/rockchip.xml
            └── meta-kickpi project
```

1. remote 和唯一 default 在 remotes.xml 定义，由产品入口引入一次。
2. base/ 管公共项目，不包含厂商和板卡。
3. bsp/ 管芯片平台上游仓库与必要工具，不包含 base。
4. boards/ 组合 BSP 与板级定制，不包含 base。demo 板型仍需确认。
5. products/ 是 repo init -m 的完整入口，同一板卡以后可对应多个产品。
6. releases/ 保存验收后的产品 SHA 清单，固定 SHA 不替代验收。

include name 相对 manifest 仓库根目录；project path 相对 repo 工作区根目录。
Git project 不一定等于 BitBake layer，meta-openembedded 和 meta-xilinx 均含多个子 layer。

Xilinx 项目保留显式 sync-s=true 策略，供选版时一致处理子模块；该 Wrynose 提交没有 gitlink，gen-machine-conf 是单独的按需工具，不能用这个属性代替工具仓库声明。

## 默认与集成入口

默认产品保持 K7。K7 自有 layer 尚未完成 Wrynose 移植，default 明确选择候选源码组合，repo 初始化时也会显示状态提示。
default 表示未指定 -m 时的选择，不表示生产发布认证。

integration 同样固定 SHA。依赖升级先修改候选提交，核对兼容和依赖，再做构建与目标测试。
以后 default 和 integration 版本分离时共享组成片段，通过版本覆盖或生成流程处理差异，避免两份独立项目列表。

不简单 include 所有产品来创建 all.xml，以免重复公共项目。将来需要联合工作区时，应对 BSP、板级项目去重，并确保所有产品可共享同一提交组合。

## Git 仓库边界

| 仓库 | 状态 | 职责 |
| --- | --- | --- |
| yocto-manifests | 当前仓库 | 组合、版本、同步和清单校验 |
| yocto-platform | 规划，尚无真实远程 | 初始化、profile、自有发行版、image、构建 CI |
| meta-kickpi | 已存在 | K7 MACHINE、DTS、内核、启动链 |

不添加未知 URL、占位 SHA 或 shell 变量形式的 project。复制到任意名称的新 manifest Git 仓库后，公开上游地址仍有效。

## 旧路径迁移

| 旧路径 | 新路径 |
| --- | --- |
| SDK-Yocto/ | yocto-manifests/ |
| common/base.xml | remotes.xml、base/yocto.xml、base/openembedded.xml |
| vendors/rockchip/rockchip-soc.xml | bsp/rockchip.xml |
| vendors/stm32/stm32-soc.xml | bsp/stm32.xml |
| vendors/xilinx/xilinx-base.xml | bsp/xilinx.xml |
| custom/kickpi/kickpi-common.xml | boards/kickpi-k7.xml 中的 project |
| custom/kickpi/kickpi-k7.xml | products/kickpi-k7/integration.xml |
| vendors/rockchip/rk3576/rk3576-demo.xml | products/rk3576-evb/integration.xml |
| vendors/stm32/stm32mp157/stm32mp157-demo.xml | products/stm32mp157-demo/integration.xml |
| vendors/xilinx/zynq7020/zynq7020-demo.xml | products/zynq7020-demo/integration.xml |

旧入口不保留别名。已有工作区需改用新的 -m 路径；核心由 Poky 组合仓库改为拆分项目，推荐使用空工作区并保留原工作区作对照。

