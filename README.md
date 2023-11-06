# 声明
该代码仓库为搬运，原作者详见 [https://www.52pojie.cn/thread-1852977-1-1.html] ps:我是从这里搬运的，不确定是不是真的原作者。

## Python依赖
```
aiohttp==3.8.6
aiofiles==23.2.1
lxml==4.9.3

```
## 运行

其中`PICTURE_HOST`就是写真域名，需要**科学访问**。

`PROXY` 需要填写**你使用的VPN的代理端口号**，源码里的8080是我随便写的。

运行方法很简单：`python main.py xxxx xxxx xxxx`，其中`xxxx`为姓名，多个人名按照空格隔开。

获取完毕后会在当前创建一个`Downloads`目录，图片会按照姓名以及相册名归类在里面。

## 写在最后

如果运行成功请给个 **star** ,运行失败可以在**issues**讨论。
