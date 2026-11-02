# 构建集成仓库接入方案

yocto-platform 是下一阶段独立 Git 仓库的建议名称。它尚无真实远程，因此 base/project.xml 为空，不阻断当前公开源码获取。

```text
yocto-platform/
├── scripts/
│   ├── setup-environment
│   ├── build.sh
│   └── collect-artifacts.sh
├── profiles/
│   ├── kickpi-k7-dev.conf
│   └── kickpi-k7-release.conf
├── meta-platform/
│   ├── conf/
│   │   ├── layer.conf
│   │   ├── distro/platform.conf
│   │   └── templates/default/
│   │       ├── bblayers.conf.sample
│   │       └── local.conf.sample
│   ├── recipes-core/images/
│   ├── recipes-core/packagegroups/
│   └── recipes-apps/
├── containers/
├── ci/
└── docs/
```

profile 集中选择 MACHINE、DISTRO、IMAGE 和模板；模板提供公共骨架，脚本生成配置，避免在 profile、模板、CI 中重复维护相同参数。
实际 layer 路径为 sources/yocto-platform/meta-platform。
板级 DTS、内核追加、MACHINE 继续由 meta-kickpi 维护；发行版、包集合和公共产品策略由 meta-platform 维护。

接入步骤：

1. 创建真实 Git 仓库并提交可执行的最小集成内容。
2. 必要时在 remotes.xml 添加真实地址前缀。
3. 在 base/project.xml 添加真实 name、sources/yocto-platform 路径、完整 SHA、upstream。
4. 在该 project 使用 linkfile 将 scripts/setup-environment 暴露到工作区根目录。
5. 验证脚本能定位 profile 和 layer，不依赖用户 HOME、旧仓库名或 /home/ryan 路径。
6. 配置生成到 build/<product>/，显式配置 DL_DIR、SSTATE_DIR，重新初始化不得静默覆盖已有配置。

完成后，复现范围从确定的源码组合扩展到自动初始化的产品构建。当前没有用空脚本或虚构 URL 表示此功能已实现。

