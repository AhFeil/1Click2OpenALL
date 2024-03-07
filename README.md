# 1Click2OpenALL

**一键全开**输入框中的网址。

体验网址： http://oneclickopen.vfly2.com/

![](https://ib.ahfei.blog:443/imagesbed/1Click2OpenALL-show-how-24-03-27.webp)

测试通过的浏览器：
- Windows： Edge、Chrome、Firefox、Vivaldi
- Android： Samsung Browser、


## 管理员

可以自定义加密 session 的密钥，通过添加环境变量实现

```sh
export 1Click2OpenALL_SECRET="your_secrec_key"
```

安装步骤： [一键全开 1Click2OpenALL 的安装步骤 - 技焉洲 (vfly2.com)](https://technique.vfly2.com/2024/03/deployment-process-1click2openall/)


## 使用

> **第一次使用**，点击“获取弹窗权限”的那个链接，然后允许弹窗

把含有网址的内容粘贴进输入框，然后点 Open Websites 即可。


### 支持的格式


每次检测一行。下面是按照匹配顺序列出的：
1. 一行含有网址的 md 格式文本，会提取其中所有网址
2. 使用正则寻找匹配 http://xx.xx/xxx 和 https://xx.xx/xxx 这种格式的字符串
3. 一行一个纯网址，可以省略 http://、https:// ，如果是中文域名则抛弃
4. 忽略空行

---

推荐使用，一行是一个纯网址或者是 md 格式含有网址的

```
baidu.com
blog.vfly2.com
https://blog.vfly2.com/
```


```
[承飞之咎 - Explore, Make Friends and Live Independently (vfly2.com)](https://blog.vfly2.com/) 和 [技焉洲 - Linux，单片机，编程 (vfly2.com)](https://technique.vfly2.com/)
```


使用正则匹配

```
- Rime输入法词库扩充：https://zhuanlan.zhihu.com/p/471412208
https://blog.vfly2.com/  一些文字
```

不同行可以是不同格式的


```
https://blog.vfly2.com/

baidu.com

[提供 AhFei 的 自建服务 - Emby, Bitwarden, and more - 承飞之咎 (vfly2.com)](https://blog.vfly2.com/2024/01/provide-ahfeis-self-hosted-services-emby-bitwarden-and-more/)

以下是我在寻找 vscode 文章时发现的： 
上面这种原本应该匹配的一行一个网址，但是中文域名太少用，而且中间夹杂一段无网址的文本也很常见，于是抛弃中文域名以避免这种情况

- Rime输入法词库扩充：https://zhuanlan.zhihu.com/p/471412208
```

---

*会出错的*

```
https://blog.vfly2.com/一些文字
这种中间无空格的，会把后面的文字也当作网址一部分
```