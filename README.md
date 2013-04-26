ME@deepgully
===

`ME@deepgully`是基于Python,Flask的开源博客系统,可以运行在GAE(Google AppEngine)和BAE(Baidu AppEngine)上  
`ME@deepgully` is a open source blog system based on Python&Flask, support GAE(Google AppEngine) and BAE(Baidu AppEngine)


##主要功能 Features

 1. 响应式页面,自动适应不同设备   
 Responsive design,adaptive on different devices
 2. 4种模版可选 4 Templates
    1. [Timeline](http://demo.me.deepgully.com/): 时间线 
    2. [List](http://demo.me.deepgully.com/list): 列表显示, 普通Blog的显示方式 
    3. [Photo](http://demo.me.deepgully.com/photo): 相册模式, 只显示图片
    4. [Text](http://demo.me.deepgully.com/text): 文本格式,自定义页面 
 3. 基于 **Markdown** 格式, 增强的 **Markdown** 在线编辑器 [Markdown格式说明][http://wowubuntu.com/markdown/], 实时预览    
 Based on  **Markdown**, enhancement Markdown online editor
 4. 代码高亮支持(包括评论里的代码)   
 Code highlight, support code block in comments
 5. 支持快捷键: `j`--下一个, `k`--上一个, `i`--跳回第一个, `n`--跳到最后一个, `space`--下一个(循环), `enter`--载入更多  
 Shortcut support: `j`--Next, `k`--Prev, `i`--First, `n`--Last, `space`--Next(loop), `enter`--Load More
 6. 支持多用户 
   Multi-user support


##安装说明 Install

##在GAE上安装`ME@deepgully`

#### 准备工作

 1. 申请 **GAE** 账号, 创建基于 **Python** 的 **High Replication** 应用
 2. 安装GAE Python 本地开发环境 https://developers.google.com/appengine/downloads

#### 更改设置

 1. 从 https://github.com/deepgully/me 下载ME@deepgully代码
 2. 编辑代码根目录下的app.yaml和setting.py

> 将app.yaml第一行的application id改成你自己的
    
    application: me-deepgully
    version: 1
    runtime: python27
> 编辑settings.py

> 更改默认管理员账号密码 `app.config["OwnerEmail"]` 及 `app.config["DefaultPassword"]` 

    app.config["OwnerEmail"] = "deepgully@gmail.com"
    app.config["DefaultPassword"] = "admin"

#### 上传

  1. 使用GAE SDK工具上传应用, 也可在代码根目录执行命令行 `appcfg.py update .`
  2. 搞定, 登陆之后可到管理后台更改网站标题等设置

  P.S 上传后GAE会花几分钟到几个小时创建datastore index, 请等一段时间再访问
  
#### 本地调试GAE

  1. cd到项目目录运行 `dev_appserver.py ./`
  2. 访问 http://localhost:8080


##在BAE上安装`ME@deepgully`

#### 准备工作

 1. 申请 **BAE** 账号, 创建基于 **Python** 的 **Web应用**
 2. 创建BAE云存储 **bucket** http://developer.baidu.com/bae/bcs/bucket/ , 记下 **bucket名字**
 3. 创建BAE 数据库, 记下 **数据库名字** , 注意数据库的到期时间(可以免费续费)
 4. 进入BAE应用的版本管理, 创建新版本, 使用SVN工具checkout到本地

#### 更改设置 

 1. 从 https://github.com/deepgully/me 下载ME@deepgully代码
 2. 编辑代码根目录下的settings.py

> 更改数据库设置, 将`SAE_DATABASE`改成你的数据库名字
    
    if RUNTIME_ENV in ("bae",):
        SAE_DATABASE = "qHWGMWtaVuVSNMEpprEk"

> 更改默认管理员账号密码 `app.config["OwnerEmail"]` 及 `app.config["DefaultPassword"]` 
    
    app.config["OwnerEmail"] = "deepgully@gmail.com"
    app.config["DefaultPassword"] = "admin"

> 更改BAE云存储设置,将`BUCKET_NAME`改成你刚才创建的bucket名字
    
    if RUNTIME_ENV in ("bae",):
        from bae.api import bcs
        BUCKET_NAME = "deepgully"

#### 上传

  1. 将ME@deepgully代码拷贝到BAE本地目录
  2. SVN上传所有文件
  3. 搞定, 登陆之后可到管理后台更改网站标题等设置
  
#### 本地调试BAE

  1. 安装SQLAlchemy, `pip install SQLAlchemy`
  2. 安装Flask, `pip install Flask`
  3. 安装PIL, `pip install PIL`
  4. 运行 index.py, 默认生成的sqlite数据库文件是test.db (也可以更改settings.py设置使用其他的数据库)
  5. 访问 http://localhost:5000

