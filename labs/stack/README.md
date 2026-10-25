# 贯穿实验：资料索引助手

Python 3.10+，仅标准库。默认脚本化协议夹具不是LLM。只操作临时生成的配置，不执行任意代码或Shell。

```bash
python3 run.py all
python3 -m unittest -v test_stack
```

默认结果写入`results/`，重复执行会替换同名记录。`--out`可另设目录。

真实模型接入必须显式`live --base-url ... --model ... --acknowledge-cost`；远程还需`--allow-remote`且HTTPS。密钥从AI_LAB_API_KEY读取。这里只实现Chat-Completions合同，不兼容所有模型、Responses或Anthropic原生接口。程序不自动下载模型、不自动使用付费API、不提供Harvard算力。

`serve`的HTTP夹具不加载神经网络；小模型CPU计算是另一项检查。真实GPU引擎测评保持NOT_RUN。

八个任务是公开合成夹具，heldout-demo只是切分示范；不能当秘密测试或泛化评估。耗时是真实本机运行，字节是真实序列化长度；Token与美元未知时为null。

全部课内要求见`../projects/assignment1.html`至`assignment5.html`，完整源码说明见`code.html`。
