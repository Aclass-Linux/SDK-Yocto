# 产品发布与新仓库复现

## 当前基线

manifest 开发分支为 main。目标系列为 Wrynose，不在各层目录反复添加系列名。
以后维护其它 Yocto 系列时，用独立 manifest 分支与源码工作区。

所有 revision 已固定为 SHA，但当前没有经过产品验收的发布。
integration 表示候选组合，default 表示默认选择，release 表示验收后的产品版本。

## 生成发布清单

1. 记录 manifest 仓库提交，确保工作区无未提交修改和未说明的 local manifest。
2. 按 build-matrix.md 验收源码、配置、配方源码版本、构建和目标测试。
3. 在工作区运行 `repo manifest -r -o /tmp/product-release.xml`，检查结果及 upstream、子模块策略。
4. 将审查后的完整清单放入 releases/<product>/<version>.xml，校验后在空工作区重放。
5. 为 manifest 创建产品发布 tag，记录 yocto-platform、工具、主机或容器版本及测试证据。

验证器拒绝将带 migration-status 的待迁移 BSP 放入 release。不要通过删除标注绕过移植和验收。
锁定 layer 不包含未提交修改，也不自动锁定 AUTOREV 配方的下游源码。

## 新仓库复现

上游 project 不引用 manifest 旧地址或本地目录名。将项目文件与目录提交到新 manifest Git 地址后，用新 URL 初始化：

```bash
repo init -u <new-manifest-url> -b <manifest-commit-or-tag> -m products/qemuarm64/default.xml
repo sync -c
python3 .repo/manifests/ci/verify-checkout.py --entry products/qemuarm64/default.xml
```

本地改动需先提交并推送，新地址才包含本轮工作。目录改名不会更新远端。

长期交付还需可用的 Git / 下载源码镜像及配方依赖归档。改用内部镜像时显式更新 remotes/project name，并重新做空目录同步验证。

