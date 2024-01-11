# oneclickopen

一键全开网址



## 改进





## 功能

1. 一行一个网址，可以省略 http://、https://
2. 一行可以是一段含有网址的 md 格式文本，
3. md 格式和纯网址可以一起复制进去，只要一行一种就行
4. 如果某一行既不是单纯的网址，也不包含 md 格式的网址，会被丢弃




```
baidu.com
google.com
```


```
官网： [库苏恩 (spiritlhl.net)](https://www.spiritlhl.net/)，还有 [学好kvm，从图形化到命令 (zsythink.net)](https://www.zsythink.net/archives/category/%e8%bf%90%e7%bb%b4%e7%9b%b8%e5%85%b3/kernel-based-virtual-machine)  hE：玩玩 PVE
google.com
```

```
[VikParuchuri/marker: Convert PDF to markdown quickly with high accuracy (github.com)](https://github.com/VikParuchuri/marker)
baidu.com
[astral-sh/ruff: An extremely fast Python linter and code formatter, written in Rust. (github.com)](https://github.com/astral-sh/ruff)
google.com
[Articles about Software Engineering, AI, DevOps, Cloud and more (ataiva.com)](https://ataiva.com/)
```

```
www.baidu.com

http://154.204.60.26:8002/

[承飞之咎 - Explore, Make Friends and Live Independently (vfly2.com)](https://blog.vfly2.com/)

https://blog.vfly2.com/

[提供 AhFei 的 自建服务 - Emby, Bitwarden, and more - 承飞之咎 (vfly2.com)](https://blog.vfly2.com/2024/01/provide-ahfeis-self-hosted-services-emby-bitwarden-and-more/)

https://blog.vfly2.com/2024/01/provide-ahfeis-self-hosted-services-emby-bitwarden-and-more/

以下是我在寻找 vscode 文章时发现的*不*相关阅读：

[全栈工程师为什么越混越困难，看这篇就够了](https://blog.csdn.net/huaxiangchen/article/details/106050664)
```


这种会被丢弃，即使其中有网址

```
以下是我在寻找 vscode 文章时发现的*不*相关阅读：

全栈工程师为什么越混越困难，看这篇就够了： https://blog.csdn.net/huaxiangchen/article/details/106050664
```

