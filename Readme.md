## 1.运行环境

运行环境见*requirements.txt*文件。其中：

**OpenNRE库安装方式**

```bash
git clone https://github.com/thunlp/OpenNRE.git
```

或

```bash
git clone https://github.com/thunlp/OpenNRE.git --depth 1
```

然后在opennre目录里安装所需的环境

```bash
pip install -r requirements.txt
```

**Stanza库安装方式**

stanza官方文档：https://stanfordnlp.github.io/stanza/index.html

在命令行使用如下命令即可安装

```bash
pip install stanza
```

## 2.文档说明

*analysis_data：*存放系统处理的数据结果

*scripts：*爬取的电影剧本源文本

*format_scripts：*预处理后的电影剧本文本

*ui：*系统界面文件

*scene_change_words：*英文剧本的常用场景过渡词

*main.py：*系统运行文件

## 3.运行方式

运行*main.py*文件即可