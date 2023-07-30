# simple_tieba_sign

Python3 简易一键签到百度贴吧的脚本（模拟客户端）

## 本地运行

```shell
pip install -r requirements.txt
python tieba.py #填入 BDUSS,会保存在 BDUSS.txt 文件中,下次就不需要输入了
```

## Github Action 运行签到

新建名为`BDUSS`的`Repository secrets`，每天自动运行签到，也可手动运行(github action 访问国内有点慢)

Nodejs Version: [liuxsdev/tieba_sign](https://github.com/liuxsdev/tieba_sign)
