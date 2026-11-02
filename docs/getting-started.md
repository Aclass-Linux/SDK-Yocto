# 从安装 repo 到初始化工作区

以下命令以当前 Ubuntu 26.04 环境、Bash 和现有路径为例。
当前 yocto-manifests 已是 Git 仓库，分支为 main，已有 origin；直接沿用 Git 历史提交即可。

最终目录如下：

```text
/home/ryan/Documents/Yocto/
├── yocto-manifests/           # 编辑、提交、推送 XML 的 Git 仓库
├── workspace-qemuarm64/       # repo init / sync 生成的独立工作区
│   ├── .repo/
│   └── sources/
└── workspace-kickpi-k7/       # 可选：K7 的独立工作区
```

repo 工作区通过 XML 同步多个 Git 仓库。它使用自己的 .repo/ 管理信息，不需要再对整个工作区执行 git init。
源码工作区中的 .repo/manifests/ 是清单检出，日常清单编辑仍建议在上面的 yocto-manifests/ 作者仓库进行。

## 1. 安装 repo

使用 Ubuntu 软件包：

```bash
sudo apt update
sudo apt install -y git python3 curl ca-certificates gnupg repo

git --version
python3 --version
repo version
```

安装的是 repo 启动器，第一次 repo init 会继续取得完整工具。
还没有工作区时，repo version 中出现“repo 未安装到工作区”的提示可以正常理解；应能看到 launcher 版本。
安装依据：[git-repo 官方 README](https://gerrit.googlesource.com/git-repo/+/HEAD/README.md)、[官方安装步骤](https://source.android.com/docs/setup/start/requirements#install-repo)。

如果 apt 找不到 repo，可使用官方启动器：

```bash
mkdir -p "$HOME/.local/bin"
curl -fL https://storage.googleapis.com/git-repo-downloads/repo -o "$HOME/.local/bin/repo"
chmod 755 "$HOME/.local/bin/repo"
export PATH="$HOME/.local/bin:$PATH"
repo version
```

使用手动安装方式时，把 `export PATH="$HOME/.local/bin:$PATH"` 加入 ~/.bashrc，使新终端也能找到 repo。

## 2. 提交当前 manifest 内容

```bash
cd /home/ryan/Documents/Yocto/yocto-manifests

git status --short
git branch --show-current
git remote -v
git config --get user.name
git config --get user.email
```

如 Git 姓名或邮箱尚未配置，在当前仓库设置自己的身份：

```bash
git config user.name "你的名字"
git config user.email "你的邮箱"
```

检查并提交本轮重组：

```bash
bash ci/check.sh
git diff
git add -A
git diff --cached --stat
git commit -m "Restructure Yocto manifests for Wrynose"
```

本地 repo init 和远程发布都读取 Git 提交；未提交的 XML 变更和未跟踪文件不会被它们自动采用。

## 3. 发布到 Git 远端

在 GitHub、GitLab 或自己的 Git 服务创建一个空仓库，建议名称 yocto-manifests。创建时不自动添加 README、许可证或其它初始提交，以便推送现有历史。
复制该仓库的实际 Git clone 地址，替换下面变量中的示例地址：

```bash
cd /home/ryan/Documents/Yocto/yocto-manifests
YOCTO_MANIFEST_URL='https://你的Git服务/你的组织/yocto-manifests.git'

# 当前已经存在 origin，因此更新地址。
git remote set-url origin "$YOCTO_MANIFEST_URL"
git push -u origin main

# 记录刚推送的 manifest 精确版本。
YOCTO_MANIFEST_REV=$(git rev-parse HEAD)
printf '%s\n' "$YOCTO_MANIFEST_REV"
```

若继续使用当前 origin 地址，可以跳过 set-url，改用 `YOCTO_MANIFEST_URL=$(git remote get-url origin)`。
推送需要该 Git 服务的正常认证，例如已有 SSH key 或 HTTPS 凭据。

下面沿用同一个终端中的 YOCTO_MANIFEST_URL 和 YOCTO_MANIFEST_REV；换终端后需要重新设置。

## 4. 先用 QEMU 参考入口跑通同步

从空目录初始化，使用刚推送的 manifest 提交，明确选择 QEMU 入口：

```bash
cd /home/ryan/Documents/Yocto
mkdir workspace-qemuarm64
cd workspace-qemuarm64

repo init -u "$YOCTO_MANIFEST_URL" -b "$YOCTO_MANIFEST_REV" -m products/qemuarm64/default.xml
repo sync -c -j4
repo list

python3 .repo/manifests/ci/verify-checkout.py --entry products/qemuarm64/default.xml
```

预期得到 sources/openembedded-core、sources/bitbake、sources/meta-yocto；校验应通过 3 个项目。
`-u` 是 manifest Git 地址，`-b` 是 manifest 版本，`-m` 是入口路径。
这里采用 manifest 提交保证清单本身也固定；日常跟踪最新清单时可改用 -b main。[repo 命令说明](https://source.android.com/docs/setup/reference/repo)

如果只想先在本机验证、暂不发布远端，可在完成第 2 步提交后，改用以下变量继续本步骤：

```bash
YOCTO_MANIFEST_URL=/home/ryan/Documents/Yocto/yocto-manifests
YOCTO_MANIFEST_REV=$(git -C "$YOCTO_MANIFEST_URL" rev-parse HEAD)
```

本地绝对地址只用于本机试跑；其它机器需要能访问的远端 URL。

## 5. 初始化 K7 源码工作区

K7 保持默认产品选择，使用另一个空目录：

```bash
cd /home/ryan/Documents/Yocto
mkdir workspace-kickpi-k7
cd workspace-kickpi-k7

repo init -u "$YOCTO_MANIFEST_URL" -b "$YOCTO_MANIFEST_REV" -m default.xml
repo sync -c -j4
repo list

python3 .repo/manifests/ci/verify-checkout.py --entry default.xml
```

预期 6 个项目，包括核心、meta-openembedded、meta-rockchip 与 meta-kickpi。
这是固定的源码组合。meta-kickpi 当前仍来自 Scarthgap，需先完成 Wrynose 移植，再接入产品构建配置。

## 6. 同步完成后的顺序

1. 在满足 Yocto 主机依赖的环境完成 QEMU 配方解析、参考镜像构建与启动验证。
2. 移植 K7 自有 layer 到 Wrynose，验证 machine、配方追加、设备树与启动链。
3. 创建 [yocto-platform 构建集成仓库](platform-repository.md)，交付 profile、初始化脚本和自有发行版 / image。
4. 构建、上板验收后按 [发布流程](release-process.md) 冻结产品版本。

当前主机缺少 en_US.UTF-8 locale，准备运行 BitBake 时先补齐：

```bash
sudo apt install -y locales
sudo locale-gen en_US.UTF-8
export LANG=en_US.UTF-8
export LC_ALL=en_US.UTF-8
locale -a
```

repo 安装依赖与 Yocto 编译依赖不同，完整构建前按 [Yocto 6.0 主机要求](https://docs.yoctoproject.org/6.0/ref-manual/system-requirements.html) 安装构建所需软件。
