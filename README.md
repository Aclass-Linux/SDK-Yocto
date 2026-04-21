# Manifest 模板说明

这里放的是 `repo` 的 manifest 模板, 目前按三类平台拆分:

- `default.xml`: 默认入口, 当前指向 `rk3576.xml`
- `base.xml`: 公共层
- `rk3576.xml`: Rockchip RK3576 平台层
- `stm32mp157.xml`: ST STM32MP157 平台层
- `zynq7020.xml`: Xilinx Zynq-7020 平台层

当前策略:

- 先保留最小可确认集合
- 固定采用"单源码工作区 + 多 build 目录 + 共享缓存"工程方案
- 所有未确认的公司仓库和 BSP 仓库先不放进 manifest
- 平台 XML 目前只负责引用 `base.xml`
- layer 统一直接放在工作区根目录, 不放 `sources/` 子目录

使用建议:

1. 先统一 Yocto 主线版本, 例如 `scarthgap`
2. 再确认每个平台的 BSP layer 来源
3. 最后把这些 XML 放入独立的 manifest git 仓库

注意:

- 当前已删除占位仓库和未确认仓库
- 后续新增仓库时, 一次只加确认过的仓库
- 平台专属 BSP 仓库应尽量固定到 tag 或稳定分支
