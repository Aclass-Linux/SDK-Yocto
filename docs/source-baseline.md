# 固定源码基线

记录日期：2026-11-02；K7 开发集成更新：2026-11-05。核心版本为 Yocto 6.0.4 / Wrynose；所有清单采用完整 SHA，未使用移动分支作为 revision。

## 核心官方发布

OE-Core、BitBake、meta-yocto 提交来自 [Yocto 6.0.4 官方发布说明](https://downloads.yoctoproject.org/releases/yocto/yocto-6.0.4/RELEASENOTES)。
BitBake 来源分支为 2.18，不能统一替换成 wrynose。原 Poky 组合仓库拆分依据见 [Wrynose 官方说明](https://www.yoctoproject.org/blog/2026/05/13/yocto-project-6-0-wrynose-is-here/)。

## 项目版本清单

其它 layer 是当日选择的集成快照，不表示它们属于 Yocto 6.0.4 官方发布集合，也未声称这些分支头已联合构建通过。

| 片段 | 项目 | revision | upstream |
| --- | --- | --- | --- |
| base/openembedded.xml | openembedded/meta-openembedded.git | `c734c2cb9713dbd6d50697a9f6c25ebdf3ae589e` | `refs/heads/wrynose` |
| base/yocto.xml | openembedded/openembedded-core.git | `0f03c732a0a2d0506b41b1abe60b3f368b2300dc` | `refs/heads/wrynose` |
| base/yocto.xml | openembedded/bitbake.git | `51fd94a67fa17650a9ff623492005972bbc7d26f` | `refs/heads/2.18` |
| base/yocto.xml | meta-yocto | `7c25b11156553145fa6b241a2d4f65d94438f804` | `refs/heads/wrynose` |
| bsp/rockchip.xml | JeffyCN/meta-rockchip | `f2fa9fd14571b855bb59a51da11616904a65f36d` | `refs/heads/wrynose` |
| bsp/stm32.xml | STMicroelectronics/meta-st-stm32mp.git | `a5e5cef8442de4eb3afca97e4c4dddb0f25e4ae1` | `refs/heads/wrynose_v26.02.18` |
| bsp/xilinx.xml | meta-arm | `673e8d7c5dcd14de58092eb73e6ecc5eee5c1735` | `refs/heads/wrynose` |
| bsp/xilinx.xml | meta-xilinx | `1231e93e0aa083d67ad60e9670733addcc501e92` | `refs/heads/wrynose` |
| boards/kickpi-k7.xml | Aclass-Linux/meta-kickpi.git | `bda8d1abb8210eeef0cb125f2d2a311f9af1f3b4` | `refs/heads/wrynose` |
| boards/kickpi-k7.xml | eclipse-iceoryx/meta-iceoryx2.git | `de61fae35da436e01ef0c463c6b57f57432fea36` | `refs/heads/main` |

## 来源及兼容状态

- meta-openembedded：公开仓库 wrynose 的固定集成快照，与核心发布提交分开记录。
- Rockchip：所选 wrynose layer.conf 声明 wrynose，存在 rockchip-rk3576-evb machine。
- ST：实际分支名为 wrynose_v26.02.18，其 layer.conf 声明 wrynose。
- Xilinx：所选 wrynose layer.conf 声明 wrynose。保留 sync-s=true 的显式策略，但该提交实际没有 gitlink；gen-machine-conf 已变为独立、按构建流程选择的工具仓库，不会由 sync-s 自动下载。
- K7：Wrynose 自有 BSP 与产品 layer，使用 linux-yocto 6.18 和官方 U-Boot 2026.10。annotation 标记构建检查完成、硬件待验收；meta-rockchip 仍同步作参考，不加入 K7 BBLAYERS。
- iceoryx2：官方层检出到 `sources/meta-iceoryx2`。K7 构建模板保留该层的可选入口。启用前需验证固定提交及其依赖能否在 Wrynose 上构建。

[Rockchip layer](https://github.com/JeffyCN/meta-rockchip/blob/f2fa9fd14571b855bb59a51da11616904a65f36d/conf/layer.conf)、
[ST layer](https://github.com/STMicroelectronics/meta-st-stm32mp/blob/a5e5cef8442de4eb3afca97e4c4dddb0f25e4ae1/conf/layer.conf)、
[Xilinx layer](https://git.yoctoproject.org/meta-xilinx/tree/meta-xilinx-core/conf/layer.conf?id=1231e93e0aa083d67ad60e9670733addcc501e92)、
[K7 layer](https://github.com/Aclass-Linux/meta-kickpi/blob/bda8d1abb8210eeef0cb125f2d2a311f9af1f3b4/conf/layer.conf)。

## 复现边界

相同 manifest 提交、入口与 revision 指向同一组 Git 对象；完整源码下载、构建、二进制可复现和板卡启动是不同验收阶段。
固定 manifest 不能保存未提交修改或冻结配方中的 AUTOREV。镜像、SDK、host/container 与配置基线需要按发布流程另行记录。
