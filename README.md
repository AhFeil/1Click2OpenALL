# 1Click2OpenALL

**一键全开**文本框中的网址。

体验网址： http://oneclickopen.vfly2.com/

![](https://ib.ahfei.blog:443/imagesbed/1Click2OpenALL-show-24-05-07.webp)

测试通过的浏览器：
- Windows： Edge、Chrome、Firefox、Vivaldi
- Android： Samsung Browser、


## 使用

> *第一次使用*，点击“获取弹窗权限”的那个链接，然后允许弹窗

把含有网址的内容**粘贴**进文本框，然后点 **Open Websites** 即可。

除了打开网址，它还会把这次打开的网址都显示在页面下方。


### 它是怎么提取出网址的

0. 每次检测一行，忽略空行。以下面的顺序进行匹配：
1. 一行含有网址的 md 格式文本，会提取其中所有网址
2. 使用正则寻找匹配 http://xx.xx/xxx 和 https://xx.xx/xxx 这种格式的字符串
3. 一行一个纯网址，可以省略 http://、https:// 。如果是中文域名则抛弃，因为很少见

---

推荐填入的格式：一行是一个纯网址，或者是 md 格式含有网址的

```
一行是一个纯网址的如下：
yanh.tech
blog.vfly2.com
https://blog.vfly2.com/

md 格式含有网址的如下：
[技焉洲 - Linux，单片机，编程](https://yanh.tech/) 和 [承飞之咎 - Explore, Make Friends and Live Independently (vfly2.com)](https://blog.vfly2.com/)
```


使用正则匹配的例子

```
- Rime输入法词库扩充：https://zhuanlan.zhihu.com/p/471412208
https://yanh.tech/  一些文字，如果文字不是网址一部分，请用空格分开


这种中间无空格的，会把后面的文字也当作网址一部分，因为存在这种网址
https://yanh.tech/一些文字
```


不同行可以是不同格式的，但是同一行按照匹配顺序依次检测后，检测到第一个就会返回网址，即便还有符合其他剩余模式的

```
https://yanh.tech/

yanh.tech

[信息源转 RSS 框架 - source2RSS 的安装步骤 - 技焉洲](https://yanh.tech/2024/07/deployment-process-for-source2rss/)

以下是我在寻找 vscode 文章时发现的： 
上面这种原本应该匹配的一行一个网址，但是中文域名太少用，而且中间夹杂一段无网址的文本也很常见，于是抛弃中文域名以避免这种情况

- Rime输入法词库扩充：https://zhuanlan.zhihu.com/p/471412208
```



## 管理员

> 原本使用 flask 框架，目前改用 fastAPI，并使用 htmx 实现动态加载。

可以定义跟踪代码，只需将代码放入 `templates/track.txt`，这里的代码将会插入到网页的 head 内。

安装步骤： [批量打开网址 1Click2OpenALL 的安装步骤 - 技焉洲 (yanh.tech)](https://yanh.tech/2024/03/deployment-process-1click2openall/)
