# Yocto Manifests

面向多平台的 `repo` manifest 仓库，核心基线为 **Yocto 6.0.4 / Wrynose LTS**。
原目录名 `SDK-Yocto` 现改为 `yocto-manifests`；仓库名称及本地目录名不参与源码 URL 计算，可迁移到新的 Git 地址。

首次使用请按 [从安装 repo 到初始化工作区](docs/getting-started.md) 操作，包含当前 Git 仓库的提交、远端发布与本地复现步骤。

当前交付**固定提交的源码组合**。默认仍为 KICKPI K7，其 Wrynose BSP 和产品层由同一 meta-kickpi 仓库提供，镜像与 SDK 已构建检查，真机验收尚未完成。
另提供不包含厂商 BSP 的 QEMU ARM64 核心参考入口。完整镜像编译和板卡启动尚未验收。

## 目录与职责

```text
yocto-manifests/
├── default.xml                    # K7 默认源码入口
├── remotes.xml                    # 统一地址前缀及同步并发
├── base/
│   ├── yocto.xml                  # OE-Core、BitBake、meta-yocto
│   ├── openembedded.xml           # meta-openembedded
│   └── project.xml                # 预留真实构建集成仓库接入点
├── bsp/                           # rockchip、stm32、xilinx
├── boards/                        # 板卡组合
├── products/
│   ├── kickpi-k7/                 # default.xml 与 integration.xml
│   ├── rk3576-evb/                # integration.xml
│   ├── stm32mp157-demo/            # integration.xml；具体板型待确认
│   ├── zynq7020-demo/              # integration.xml；具体板型待确认
│   └── qemuarm64/                 # default.xml；核心参考入口
├── releases/                      # 验收后的产品清单，当前没有产品发布
├── ci/                            # 离线结构与版本策略校验
├── tests/                         # 错误组合和发布门禁的回归测试
└── docs/                          # 架构、版本来源、构建矩阵及迁移说明
```

产品入口包含一次公共基础，再引入板卡；板卡引用 BSP，BSP 不反向包含基础。
所有 project 使用完整 SHA；upstream 只说明来源分支。集成入口升级也要显式更新 SHA，不会自动随上游移动。

## 在空目录复现源码

先准备 repo、Git、Python 3.10 或更高版本和公开上游网络访问。
将本仓库内容提交并推送到实际 Git 地址后执行以下命令。`<manifest-url>` 可使用新仓库地址，main 是 manifest 自身的分支。

```bash
mkdir yocto-workspace
cd yocto-workspace

# 默认 K7 开发集成源码；真机及量产资格仍待验收。
repo init -u <manifest-url> -b main
repo sync -c
repo list
```

同步后，在工作区根目录核对当前入口、每个项目的 HEAD、工作树及子模块：

```bash
python3 .repo/manifests/ci/verify-checkout.py --entry default.xml
```

使用其它入口时，--entry 填写同一个 -m 路径。

其它入口在各自空工作区选择下面的一条初始化命令，再执行 `repo sync -c`：

```bash
repo init -u <manifest-url> -b main -m products/qemuarm64/default.xml
repo init -u <manifest-url> -b main -m products/kickpi-k7/integration.xml
repo init -u <manifest-url> -b main -m products/rk3576-evb/integration.xml
repo init -u <manifest-url> -b main -m products/stm32mp157-demo/integration.xml
repo init -u <manifest-url> -b main -m products/zynq7020-demo/integration.xml
```

入口路径相对 manifest 仓库根目录，不能省略 products/。
重放某一次清单时，把 `-b main` 换为 manifest 的具体提交或 tag；移动的 main 会允许以后采用新的清单。
长期交付还应保存上游源码镜像，SHA 固定不保证公开服务器永久保留对象。

## 同步后的工作区

```text
yocto-workspace/
├── .repo/manifests/               # 本 manifest 仓库的检出
├── sources/
│   ├── openembedded-core/
│   ├── bitbake/
│   ├── meta-yocto/
│   ├── meta-openembedded/          # 按入口选择
│   └── ...                        # BSP 与板级仓库
├── build/<product>/               # 后续由构建流程生成
└── artifacts/<product>/<version>/  # 后续收集镜像、SDK、版本记录
```

没有旧的 sources/poky。repo 不设置 MACHINE、DISTRO、BBLAYERS，也不生成镜像。
base/project.xml 是有说明的空扩展点，尚未接入 yocto-platform，根目录不会自动出现 setup-environment。
独立集成仓库的内容和接入步骤见 [构建集成仓库方案](docs/platform-repository.md)。

仅同步 QEMU 入口后，可在满足 [Yocto 主机要求](https://docs.yoctoproject.org/6.0/ref-manual/system-requirements.html) 的机器上继续参考构建：

```bash
# 从该 repo 工作区根目录运行。
mkdir -p build
source sources/openembedded-core/oe-init-build-env build/qemuarm64
MACHINE=qemuarm64 bitbake core-image-minimal
```

这是 OE-Core 默认配置的参考步骤，完整镜像和启动验证见 [构建矩阵](docs/build-matrix.md)。
K7 使用 sources/meta-kickpi/layers/meta-product-k7/conf/templates/k7-upstream 模板，
具体步骤见该仓库 docs/product-layer.md。其它 demo 仍需确定具体板卡配置。

## 本地检查

```bash
bash ci/check.sh
python3 ci/validate-manifests.py products/kickpi-k7/integration.xml
```

覆盖 XML/include、项目与路径冲突、remote、完整 SHA、upstream、Xilinx 显式同步策略、README 入口和待迁移 BSP 的发布门禁。
校验器支持当前使用的 XML 子集，不能替代官方 repo 解析、真实同步及 BitBake 构建。

迁移到新 Git 服务时保留项目结构即可，上游 URL 与本 manifest 自身的地址独立。
新地址需包含提交后的清单文件才能复现。

## 文档

- [从安装 repo 到初始化工作区](docs/getting-started.md)
- [目录架构与旧路径迁移](docs/architecture.md)
- [固定版本来源](docs/source-baseline.md)
- [构建矩阵](docs/build-matrix.md)
- [构建集成仓库方案](docs/platform-repository.md)
- [发布与迁移流程](docs/release-process.md)
