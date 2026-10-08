# 在 Windows 同步到 F:\淘项

准备 Git 和 Python 3.11+，通过 Git 的凭据管理器登录有权限访问仓库的 GitHub 账号。以下为 PowerShell 指令；云端不能直接访问你的 F 盘，Windows 步骤尚未在你的电脑执行。

## 首次下载

确认存在 F 盘，且目标目录不存在，再执行：

```powershell
if (-not (Test-Path 'F:\')) { throw '没有 F 盘，请选择实际目录' }
if (Test-Path 'F:\淘项') { throw '目录已经存在，请先按下文检查，不要覆盖' }
git clone https://github.com/lubenwei96/taobao_qianniu.git 'F:\淘项'
```

若 `F:\淘项` 已存在，在该目录执行 `git status`、`git remote -v`，确认它是正确仓库且没有待保护的本地修改。普通文件夹或另一个仓库不能直接覆盖；先备份，或选择新的空路径克隆。

## 检查工具

```powershell
Set-Location 'F:\淘项'
py -3 --version
py -3 -m unittest discover -s tests -v
py -3 -m taoxiang --help
```

Python 需不低于 3.11；若没有 `py` 启动器，使用指向正确版本的 `python`。

假设利润案例（不是实际商品数据）：

```powershell
py -3 -m taoxiang --price 100 --purchase 30 --packaging 2 --shipping 5 --fee-rate 0.05 --advertising 8 --aftersales 3 --fixed 100 --orders 50
```

## 日常同步

开始修改前：

```powershell
git status
git pull --ff-only origin main
```

存在本地改动时，先备份并提交可公开的修改，再同步；不要覆盖。`--ff-only` 遇到分叉会停止，这时检查历史，在保留本地工作的前提下合并。冲突时逐个文件合并、检查并测试，不能用丢弃本地改动的方式解决。

完成修改后，指定你实际修改的非敏感文件：

```powershell
git add README.md
git diff --cached
git commit -m 'docs: update collaboration notes'
git push origin main
```

这是示例，只有 README 确实修改时才会产生提交。首次提交需要你设置自己的 Git 姓名和邮箱。不要把凭据写入仓库，不要使用 `git add -f` 添加私人数据。

换到其他电脑时重新克隆同一仓库，也可选择非 F 盘路径。私人数据按照 [数据边界](data-policy.md) 另行同步。Git 提交已推送不代表新电脑已下载；在新电脑执行 pull 与测试才完成当地验证。
