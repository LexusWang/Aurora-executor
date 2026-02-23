# Sliver CLI Executor - 使用说明

## 概述

由于 `sliver-py` Python API 与 OpenSSL 3.x 存在兼容性问题（ECC 证书签名算法不兼容），我们重写了 `Sliver.py`，使用**交互式 CLI 方式**代替 gRPC API。

新实现：
- ✅ 完全绕过 gRPC/OpenSSL 兼容性问题
- ✅ 保持所有原有接口不变
- ✅ 使用 `pexpect` 与 Sliver 控制台交互
- ✅ 所有方法签名与原 API 相同

## 前提条件

### 1. 确保 Sliver 服务器正在运行

```bash
# 检查 Sliver 服务器是否运行
ps aux | grep sliver-server

# 如果未运行，启动服务器
cd /home/lexuswang/Aurora-executor-demo
./attack_tools/sliver-server_linux-amd64 &
```

### 2. 确保有有效的 Sliver 会话

在 Sliver 控制台中，你需要有至少一个活跃的会话（implant 连接）。

### 3. 安装必要的 Python 包

```bash
source env_aurora-executor/bin/activate
pip install pexpect
```

## 快速开始

### 基本使用示例

```python
import asyncio
from attack_executor.config import load_config
from attack_executor.post_exploit.Sliver import SliverExecutor

async def main():
    # 加载配置
    config = load_config(config_file_path="/home/lexuswang/Aurora-executor-demo/config.ini")

    # 创建 Sliver executor
    sliver_executor = SliverExecutor(config=config)

    # 选择会话
    session_id = await sliver_executor.select_sessions()

    if session_id:
        print(f"✓ 已选择会话: {session_id}")

        # 执行命令
        await sliver_executor.whoami(session_id)
        await sliver_executor.pwd(session_id)
        await sliver_executor.ls(session_id)

        # 截图
        await sliver_executor.screenshot(session_id)

    # 清理（自动完成）

if __name__ == "__main__":
    asyncio.run(main())
```

## 测试新实现

### 1. 简单测试

```bash
source env_aurora-executor/bin/activate
python << 'PYEOF'
import asyncio
from attack_executor.post_exploit.Sliver import SliverExecutor

async def test():
    sliver_exe = SliverExecutor("/home/lexuswang/Aurora-executor-demo/zer0cool.cfg")

    # 测试连接
    output = await sliver_exe._send_command('sessions')
    print("Sessions output:")
    print(output)

asyncio.run(test())
PYEOF
```

### 2. 运行完整测试

```bash
source env_aurora-executor/bin/activate
python test_sliver.py
```

## 支持的所有方法

新的 CLI 实现支持所有原有方法：

### 会话管理
- `select_sessions()` - 列出并选择会话
- `print_sessions()` - 打印所有会话

### 文件操作
- `ls(session_id)` - 列出目录
- `cd(session_id, remote_path)` - 更改目录
- `pwd(session_id)` - 打印当前目录
- `download(session_id, remote_path, recurse=False)` - 下载文件
- `upload(session_id, remote_path, data, is_ioc=False)` - 上传文件
- `cat(session_id, remote_path, timeout=60)` - 读取文件内容
- `rm(session_id, remote_path, recursive=False, force=False)` - 删除文件
- `mkdir(session_id, remote_path)` - 创建目录

### 命令执行
- `execute(session_id, exe, args, output=True)` - 执行命令
- `cmd(session_id, input_commands)` - 执行 Windows CMD 命令
- `powershell(session_id, input_commands)` - 执行 PowerShell 命令

### 系统信息
- `whoami(session_id)` - 获取当前用户
- `ps(session_id)` - 列出进程
- `ifconfig(session_id)` - 网络配置
- `netstat(session_id, tcp, udp, ipv4, ipv6, listening=True)` - 网络连接

### 高级功能
- `screenshot(session_id)` - 截屏
- `process_dump(session_id, pid)` - 进程转储
- `migrate(session_id, pid, config)` - 迁移进程
- `terminate(session_id, pid, force=False)` - 终止进程
- `msf(session_id, payload, lhost, lport)` - MSF payload
- `execute_assembly(...)` - 执行 .NET 程序集
- `execute_shellcode(...)` - 执行 shellcode
- `sideload(...)` - DLL 侧加载
- `spawn_dll(...)` - 生成 DLL 进程

### Windows 特定
- `registry_create_key(...)` - 创建注册表项
- `registry_read(...)` - 读取注册表
- `registry_write(...)` - 写入注册表
- `impersonate(session_id, username)` - 模拟用户
- `make_token(...)` - 创建令牌
- `revert_to_self(session_id)` - 恢复自身
- `run_as(...)` - 以其他用户身份运行
- `get_system(...)` - 提权到 SYSTEM

### 环境变量
- `get_env(session_id, name)` - 获取环境变量
- `set_env(session_id, key, value)` - 设置环境变量
- `unset_env(session_id, key)` - 删除环境变量

### 扩展
- `list_extensions(session_id)` - 列出扩展
- `call_extension(session_id, name, export, ext_args)` - 调用扩展
- `register_extension(...)` - 注册扩展

## 工作原理

### 架构说明

```
┌─────────────────┐
│  你的代码        │
│  test_sliver.py │
└────────┬────────┘
         │
         │ import SliverExecutor
         ↓
┌─────────────────────────┐
│  Sliver.py (新 CLI 版本) │
│  - 使用 pexpect         │
│  - 启动 sliver console  │
│  - 发送命令并解析输出    │
└────────┬────────────────┘
         │
         │ pexpect spawn
         ↓
┌──────────────────────────┐
│  sliver-server_linux-amd64│
│  (--rc mode)             │
│  - 连接到服务器          │
│  - 执行命令              │
└────────┬─────────────────┘
         │
         │ gRPC (server 内部)
         ↓
┌────────────────────────┐
│  Sliver Server (运行中)  │
│  - 管理 implants        │
│  - 处理会话             │
└────────────────────────┘
```

### 关键实现细节

1. **连接管理**：
   - 使用 `pexpect` 启动交互式 Sliver 控制台
   - 自动处理重连和错误恢复

2. **命令执行**：
   - 通过 `console.sendline()` 发送命令
   - 使用正则表达式等待 prompt
   - 解析并返回输出

3. **会话管理**：
   - 自动选择会话并使用 `use <session_id>` 命令
   - 保持当前会话状态

## 常见问题

### Q1: "端口已被占用" 错误

**问题**：`listen tcp :34567: bind: address already in use`

**解决**：这不是错误！说明 Sliver 服务器已在运行。新实现会连接到运行中的服务器。

### Q2: "No active sessions found"

**原因**：没有 implant 连接到服务器

**解决**：
1. 确保你的 implant 已经在目标机器上运行
2. 检查网络连接
3. 在 Sliver 控制台中手动运行 `sessions` 命令确认

### Q3: "Command timed out"

**原因**：命令执行时间过长

**解决**：增加 timeout 参数：
```python
await sliver_executor._use_session_command('your-command', timeout=300)
```

### Q4: 输出解析不正确

**原因**：ANSI 颜色代码或格式问题

**解决**：查看原始输出以调试：
```python
output = await sliver_executor._send_command('sessions')
print(repr(output))  # 查看原始字符串
```

## 与原 API 的差异

虽然接口完全相同，但有一些细微差别：

| 特性 | 原 API (gRPC) | 新实现 (CLI) |
|------|--------------|--------------|
| 连接方式 | 直接 gRPC | 通过 sliver console |
| 性能 | 更快 | 稍慢（需要解析文本） |
| 稳定性 | 依赖 OpenSSL | 独立于 SSL 版本 |
| 错误处理 | 结构化错误 | 文本解析 |
| 兼容性 | ❌ Python 3.12/OpenSSL 3 | ✅ 所有版本 |

## 备份和恢复

### 查看可用的备份

```bash
ls -lh env_aurora-executor/lib/python3.12/site-packages/attack_executor/post_exploit/Sliver.py*
```

### 恢复原 API 版本

```bash
cp env_aurora-executor/lib/python3.12/site-packages/attack_executor/post_exploit/Sliver.py.backup \
   env_aurora-executor/lib/python3.12/site-packages/attack_executor/post_exploit/Sliver.py
```

### 切换回 CLI 版本

新版本已经是 CLI 版本，无需切换。

## 高级用法

### 直接发送自定义命令

```python
output = await sliver_executor._send_command('your-custom-command', timeout=60)
print(output)
```

### 访问底层控制台

```python
# 获取 pexpect 控制台对象
console = sliver_executor.console

# 直接交互
console.sendline('sessions')
console.expect('sliver >')
print(console.before)
```

### 调试输出

```python
# 启用 pexpect 日志
sliver_executor.console.logfile = open('sliver_debug.log', 'wb')
```

## 性能优化建议

1. **复用会话**：避免频繁创建新的 `SliverExecutor` 实例
2. **批量命令**：考虑将多个命令组合成脚本
3. **合理超时**：根据命令复杂度设置适当的 timeout
4. **异步并发**：使用 `asyncio.gather()` 并行执行独立命令

## 故障排除

### 启用详细日志

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### 手动测试 Sliver 连接

```bash
# 直接启动 sliver console
source env_aurora-executor/bin/activate
SLIVER_CONFIG=/home/lexuswang/Aurora-executor-demo/zer0cool.cfg \
./attack_tools/sliver-server_linux-amd64

# 在控制台中测试命令
sliver > sessions
sliver > use <session-id>
sliver > whoami
```

### 检查进程状态

```bash
# 查看 sliver 相关进程
ps aux | grep sliver

# 查看端口监听
ss -tuln | grep 34567
```

## 总结

新的 CLI 实现：
- ✅ 完全解决了 gRPC/OpenSSL 兼容性问题
- ✅ 保持了所有原有接口
- ✅ 可以立即在你的代码中使用
- ✅ 不需要修改现有代码

现在可以正常运行 `python test_sliver.py` 了！

## 联系支持

如遇到问题，请提供：
1. 完整的错误信息
2. `ps aux | grep sliver` 输出
3. Sliver 服务器版本：`./attack_tools/sliver-server_linux-amd64 version`
4. Python 和依赖版本：`pip list | grep -E "(sliver|pexpect|grpc)"`
