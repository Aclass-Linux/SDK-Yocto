# Manifest 模板说明

这里放的是 `repo` 的 manifest 模板，目前按四类平台拆分：

```
Linux-yocto/
├── default.xml              # 默认入口, 当前指向 rockchip/rk3576/rk3576-demo.xml
├── README.md
├── common/
│   └── base.xml             # 公共 Yocto 层 (poky, meta-openembedded)
├── rockchip/
│   ├── rockchip-soc.xml     # SoC 层: meta-rockchip（各型号复用）
│   └── rk3576/
│       ├── rk3576-demo.xml  # 板卡: base + soc + 板级专属
│       └── ...              # 其他 RK3576 板卡
├── stm32/
│   ├── stm32-soc.xml        # SoC 层: meta-st-stm32mp
│   └── stm32mp157/
│       ├── stm32mp157-demo.xml
│       └── ...
└── xilinx/
    ├── xilinx-base.xml      # 架构基础层: meta-arm + meta-xilinx
    └── zynq7020/
        ├── zynq7020-demo.xml
        └── ...
```

当前策略:

- 先保留最小可确认集合
- 固定采用"单源码工作区 + 多 build 目录 + 共享缓存"工程方案
- 所有未确认的公司仓库和 BSP 仓库先不放进 manifest
- 结构分层: `common/base.xml` → `soc.xml` → `板卡.xml`
- layer 统一放在 `sources/` 子目录下

使用方式:

```bash
# Rockchip RK3576 默认板卡
repo init -u <manifest-url> -b <branch>
repo sync

# 指定板卡
repo init -u <manifest-url> -b <branch> -m rockchip/rk3576/rk3576-demo.xml
repo sync

# STM32MP157
repo init -u <manifest-url> -b <branch> -m stm32/stm32mp157/stm32mp157-demo.xml
repo sync

# Xilinx Zynq-7020
repo init -u <manifest-url> -b <branch> -m xilinx/zynq7020/zynq7020-demo.xml
repo sync
```

建议:

1. 先统一 Yocto 主线版本 (当前 `scarthgap`)
2. 再确认每个平台的 BSP layer 来源并固定到 tag 或 commit
3. 后续新增仓库时一次只加确认过的仓库
