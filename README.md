# Manifest 模板说明

这里放的是 `repo` 的 manifest 模板, 目前按三类平台拆分:

- `default.xml`: 默认入口, 当前指向 `rk3576.xml`
- `base.xml`: 公共层
- `rk3576.xml`: Rockchip RK3576 平台层
- `stm32mp135.xml`: ST STM32MP135 平台层
- `zynq7020.xml`: Xilinx Zynq-7020 平台层

使用建议:

1. 先统一 Yocto 主线版本, 例如 `scarthgap`
2. 再确认每个平台的 BSP layer 来源
3. 最后把这些 XML 放入独立的 manifest git 仓库

注意:

- 这里的仓库地址很多还是占位符
- 你需要把 `git.example.com` 和 `your-org` 替换成真实地址
- 平台专属 BSP 仓库应尽量固定到 tag 或稳定分支
