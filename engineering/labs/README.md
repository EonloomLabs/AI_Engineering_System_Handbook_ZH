# 复现环境

实际运行：Python 3.13.5、PyTorch 2.10.0+cpu、pytest 9.0.2、SQLite 3.46.1、Git 2.47.3，Linux，CUDA不可用。

先确保 Python 环境可导入 torch、pytest，并且命令行能找到 git；再执行 `python run.py`。本教材不自动安装软件。PyTorch 应按官方安装说明选择适合操作系统的 CPU/CUDA 发行包；阅读教材不需要安装它。

程序只使用临时本地文件/数据库/Git仓库。crash_worker.py 中 os._exit(17) 是有意注入的子进程故障，不是主进程失败。Windows 符号链接和 Git 可用性不同，本次没有验证 Windows/macOS。

run.json 中的 source_sha256 用于核对运行记录与这三个 .py 文件是否一致。逻辑模拟不等于对应云端服务已经测试。
