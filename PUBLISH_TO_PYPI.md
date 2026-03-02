# Attack-Executor PyPI 发布指南

本文档记录如何将 attack-executor 库更新并发布到 PyPI 的完整流程。

## 📋 前置准备（首次发布需要）

### 1. 注册 PyPI 账号
- 访问 https://pypi.org/account/register/
- 注册账号并验证邮箱

### 2. 生成 API Token
- 登录后访问 https://pypi.org/manage/account/token/
- 点击 "Add API token"
  - Token name: `attack-executor-upload`
  - Scope: 选择 "Entire account"（首次上传）或 "Project: attack-executor"（后续更新）
- **重要**：立即复制 token（格式：`pypi-AgEI...`），它只显示一次

### 3. 配置本地认证（推荐）
创建 `~/.pypirc` 文件：

```bash
cat > ~/.pypirc << 'EOF'
[pypi]
  username = __token__
  password = pypi-AgEI...（替换为你的完整token）
EOF

chmod 600 ~/.pypirc
```

### 4. 安装发布工具
```bash
pip install --upgrade build twine
```

## 🔄 发布新版本流程

### 步骤 1: 更新版本号
编辑 `pyproject.toml`，修改版本号：

```toml
[project]
name = "attack_executor"
version = "0.2.8"  # 更新版本号
```

版本号规则：
- **补丁版本** (0.2.6 → 0.2.7): 修复 bug
- **次要版本** (0.2.7 → 0.3.0): 添加新功能，保持向后兼容
- **主要版本** (0.3.0 → 1.0.0): 重大更改，可能不向后兼容

### 步骤 2: 更新 auto_deploy.sh
如果需要，更新 `auto_deploy.sh` 中的版本号：

```bash
# 第15行
$VENV_NAME/bin/pip install attack-executor==0.2.8 \
    questionary==2.1.0
```

### 步骤 3: 提交代码更改到 Git
```bash
cd /Users/lexus/projects/Aurora-executor

# 查看更改
git status
git diff

# 提交更改
git add .
git commit -m "Update to version 0.2.8

- 描述主要更改
- 添加的新功能
- 修复的bug

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"

# 推送到 GitHub
git push origin main
```

### 步骤 4: 清理旧构建文件
```bash
rm -rf dist/ build/ *.egg-info attack_executor.egg-info
```

### 步骤 5: 构建分发包
```bash
python -m build
```

成功后会在 `dist/` 目录生成两个文件：
- `attack_executor-0.2.x-py3-none-any.whl` (wheel 包)
- `attack_executor-0.2.x.tar.gz` (源码包)

验证构建：
```bash
ls -lh dist/
```

### 步骤 6: 上传到 PyPI

**方式 1：使用配置的 .pypirc（推荐）**
```bash
python -m twine upload dist/*
```

**方式 2：直接指定 token**
```bash
python -m twine upload dist/* -u __token__ -p pypi-AgEI...（你的token）
```

**方式 3：先上传到 Test PyPI 测试（可选）**
```bash
# 上传到测试环境
python -m twine upload --repository testpypi dist/*

# 从测试环境安装验证
pip install --index-url https://test.pypi.org/simple/ attack-executor==0.2.8
```

### 步骤 7: 验证发布成功

1. **检查 PyPI 页面**
   - 访问 https://pypi.org/project/attack-executor/
   - 确认新版本已显示

2. **测试安装**
   ```bash
   # 在新的虚拟环境中测试
   python -m venv test_env
   source test_env/bin/activate
   pip install attack-executor==0.2.8

   # 验证安装
   python -c "import attack_executor; print(attack_executor.__version__)"

   # 清理
   deactivate
   rm -rf test_env
   ```

3. **测试 auto_deploy.sh**
   ```bash
   # 在测试机器上运行
   bash auto_deploy.sh
   ```

### 步骤 8: 创建 Git Tag（可选但推荐）
```bash
# 创建版本标签
git tag -a v0.2.8 -m "Release version 0.2.8"

# 推送标签到 GitHub
git push origin v0.2.8

# 或推送所有标签
git push origin --tags
```

## 📝 常见问题

### Q1: 上传失败 - "File already exists"
**原因**: PyPI 不允许覆盖已发布的版本。

**解决方案**:
- 增加版本号（即使只是修改一个字符也要升级版本）
- 删除 dist/ 目录，修改版本号后重新构建

### Q2: 导入错误 - "No module named 'attack_executor'"
**原因**: 包结构或 pyproject.toml 配置问题。

**解决方案**:
- 检查 `pyproject.toml` 中的 `[tool.setuptools.packages.find]` 配置
- 确保 `attack_executor/__init__.py` 存在

### Q3: 依赖安装失败
**原因**: pyproject.toml 中的依赖版本冲突。

**解决方案**:
- 检查 `dependencies` 列表
- 使用宽松的版本约束（如 `>=0.0.19` 而不是 `==0.0.19`）

### Q4: 构建时出现 "Multiple top-level packages" 错误
**原因**: 项目根目录有多个包目录。

**解决方案**:
pyproject.toml 应该包含：
```toml
[tool.setuptools.packages.find]
include = ["attack_executor*"]
exclude = ["attack_chains*", "attack_tools*", "test*"]
```

## 🔒 安全注意事项

1. **保护 API Token**:
   - 不要将 token 提交到 Git
   - 不要在公开场合分享
   - 定期轮换 token

2. **检查 .gitignore**:
   ```
   # .gitignore 应包含
   dist/
   build/
   *.egg-info/
   .pypirc  # 如果不小心创建在项目目录
   ```

3. **代码审查**:
   - 发布前仔细检查要打包的文件
   - 使用 `tar -tzf dist/attack_executor-0.2.x.tar.gz` 查看包内容
   - 确保不包含敏感信息（密钥、密码、内部 IP 等）

## 📚 参考资料

- [PyPI 官方文档](https://packaging.python.org/tutorials/packaging-projects/)
- [Setuptools 文档](https://setuptools.pypa.io/en/latest/)
- [版本号规范 (Semantic Versioning)](https://semver.org/)
- [Python 打包用户指南](https://packaging.python.org/)

## 🎯 快速命令参考

```bash
# 完整发布流程（复制粘贴版）
cd /Users/lexus/projects/Aurora-executor

# 1. 更新版本号（手动编辑 pyproject.toml）

# 2. 清理和构建
rm -rf dist/ build/ *.egg-info attack_executor.egg-info
python -m build

# 3. 检查构建结果
ls -lh dist/

# 4. 上传到 PyPI
python -m twine upload dist/*

# 5. 提交到 Git
git add .
git commit -m "Release version X.Y.Z"
git tag -a vX.Y.Z -m "Release version X.Y.Z"
git push origin main --tags

# 6. 验证安装
pip install --upgrade attack-executor
```

## 📅 版本历史

| 版本 | 发布日期 | 主要更改 |
|------|----------|----------|
| 0.2.7 | 2026-03-02 | 初始 PyPI 发布，包含核心功能 |
| 0.2.6 | 2025-09-15 | 内部版本，未发布到 PyPI |

---

**最后更新**: 2026-03-02
**维护者**: Lexus Wang (lingzhiwang2025@u.northwestern.edu)
