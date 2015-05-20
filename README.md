ME@deepgully
===

`ME@deepgully`是基于Python,Flask的开源博客系统,可以运行在GAE(Google AppEngine), BAE(Baidu AppEngine)和SAE(Sina AppEngine)上  
`ME@deepgully` is a open source blog system based on Python&Flask, support GAE(Google AppEngine), BAE(Baidu AppEngine) and SAE(Sina AppEngine)
 
 * Demo on GAE: http://me.deepgully.com
 * Demo on VPS: http://demo.deepgully.com
 * Demo on SAE: http://deepgully.sinaapp.com

##主要功能 Features

 1. 响应式页面,自动适应不同设备   
 Responsive design,adaptive on different devices
 2. 4种模版可选 4 Templates
    1. [Timeline](http://demo.deepgully.com/): 时间线 
    2. [List](http://demo.deepgully.com/list): 列表显示, 普通Blog的显示方式 
    3. [Photo](http://demo.deepgully.com/photo): 相册模式, 只显示图片
    4. [Text](http://demo.deepgully.com/text): 文本格式,自定义页面 
 3. 基于 **Markdown** 格式, 增强的 **Markdown** 在线编辑器 [Markdown格式说明][http://wowubuntu.com/markdown/], 实时预览    
 Based on  **Markdown**, enhancement Markdown online editor
 4. 代码高亮支持(包括评论里的代码)   
 Code highlight, support code block in comments
 5. 支持快捷键: `j`--下一个, `k`--上一个, `i`--跳回第一个, `n`--跳到最后一个, `space`--下一个(循环), `enter`--载入更多  
 Shortcut support: `j`--Next, `k`--Prev, `i`--First, `n`--Last, `space`--Next(loop), `enter`--Load More
 7. 支持外观主题, 内置16套主题 (基于Bootstrap3)   
 Themes support, 16 bootstrap3 themes builtin  
 6. 支持多用户   
 Multi-user support  
 7. 支持GAE, BAE和SAE   
 Support GAE, BAE and SAE


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

> [***重要***]: 把`app.secret_key`改成你自己生成的随机字符串

    elif RUNTIME_ENV in ("gae", "gae_dev"):
        app.secret_key = "ME@deepgully+GAE"   # 密码, cookie将使用这个key来加密

#### 本地调试GAE

  1. cd到项目目录运行 `dev_appserver.py ./`
  2. 访问 http://localhost:8080
  
#### 上传

  1. 使用GAE SDK工具上传应用, 也可在代码根目录执行命令行 `appcfg.py update .`
  2. 搞定, 登陆之后可到管理后台更改网站标题等设置

  P.S 上传后GAE会花几分钟到几个小时创建datastore index, 请等一段时间再访问
  



##在BAE上安装`ME@deepgully`

#### 准备工作

 1. 申请 **BAE** 账号, 创建工程, 解决方案选中"使用BAE"  
   BAE3 新手入门:  http://developer.baidu.com/wiki/index.php?title=docs/cplat/bae/start
 2. 创建BAE云存储 **bucket** http://developer.baidu.com/bae/bcs/bucket/ , 记下 **bucket名字**
 3. 进入BAE3应用管理控制台
 4. 在扩展服务中添加BAE MySQL数据库, 记下 **数据库ID**
 5. 在扩展服务中添加Cache服务, 记下 **Cache ID**
 6. 添加新部署(选择python-web), 使用SVN或GIT工具将代码checkout到本地

#### 更改设置 

 1. 从 https://github.com/deepgully/me 下载ME@deepgully代码
 2. 编辑代码根目录下的 **settings.py**

> 更改设置, 修改`APP_ID`, `ACCESS_KEY`, `SECRET_KEY`, `CACHE_ID`, `MYSQL_DATABASE` 
    
    if RUNTIME_ENV in ("bae",):
        const = MagicDict()
        const.APP_ID = "2929012"
        const.ACCESS_KEY = "YCiKuHCPd62DyeEtpG3c2h7y"
        const.SECRET_KEY = "dpgazAGGB4724FgvPslu7sUzkwNFesEb"
        
        const.CACHE_ID = "bTXWvXunneyHgLlmglxn"
        #...
        const.MYSQL_DATABASE = "GdCYGKgTwfbhXgAUOJcy"
        #...
               
> 更改默认管理员账号密码 `app.config["OwnerEmail"]` 及 `app.config["DefaultPassword"]` 
    
    app.config["OwnerEmail"] = "deepgully@gmail.com"
    app.config["DefaultPassword"] = "admin"

> 更改BAE云存储设置,将`BCS_BUCKET`改成你刚才创建的bucket名字, `BSC_FOLDER`也可以修改
    
    const.BCS_BUCKET = "deepgully"
    const.BSC_FOLDER = "/photos/"

#### 上传

  1. 将ME@deepgully代码拷贝到BAE本地目录
  2. SVN/GIT上传所有文件
  3. 搞定, 登陆之后可到管理后台更改网站标题等设置
  
#### 本地调试BAE

  1. 安装SQLAlchemy, `pip install SQLAlchemy`
  2. 安装Flask, `pip install Flask`
  3. 安装PIL, `pip install PIL`
  4. 运行 index.py, 默认生成的sqlite数据库文件是test.db 
  5. 访问 http://localhost:5000

>P.S. 可以更改`app.config['SQLALCHEMY_DATABASE_URI']`设置使用其他的数据库

    elif RUNTIME_ENV in ("local",):
        LOCAL_DATABASE = "test"
    
        app.secret_key = "ME@deepgully"
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///%s.db' % LOCAL_DATABASE
        #app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://test:123456@test_server:3306/%s' % LOCAL_DATABASE
     
  
##在SAE上安装`ME@deepgully`

#### 准备工作

 1. 申请 **SAE** 开发账号, 创建Python Web应用  
   SAE 新手入门:  http://sae.sina.com.cn/doc/tutorial/index.html
 2. 进入SAE应用管理控制台
 3. 在服务管理中创建SAE云存储 **domain**, 记下 **domain名字**
 4. 在服务管理中初始化MySQL数据库
 5. 在服务管理中初始化Memcache
 6. 使用SVNT工具将代码checkout到本地

#### 更改设置 

 1. 从 https://github.com/deepgully/me 下载ME@deepgully代码
 2. 编辑代码根目录下的 **config.yaml** 和  **settings.py**       

> 将config.yaml第一行的application id改成你自己的
    
    name: deepgully
    version: 1

> 编辑settings.py

> 更改默认管理员账号密码 `app.config["OwnerEmail"]` 及 `app.config["DefaultPassword"]` 
    
    app.config["OwnerEmail"] = "deepgully@gmail.com"
    app.config["DefaultPassword"] = "admin"

> 更改SAE云存储设置,将`SAE_BUCKET`改成你刚才创建的domain名字, `SAE_FOLDER`也可以修改
    
    const.SAE_BUCKET = "deepgully"
    const.SAE_FOLDER= "/photos/"

#### 上传

  1. 将ME@deepgully代码拷贝到SAE本地目录
  2. SVN上传所有文件
  3. 搞定, 登陆之后可到管理后台更改网站标题及管理员密码等设置
  
#### 本地调试 同BAE


##七牛云存储设置

0. 申请七牛帐号, 并新建存储空间 https://portal.qiniu.com/tutorial/index 

1. 使用七牛保存上传的图片

> 更改settings.py, 将`Enabled`改为`True`, 并修改`ACCESS_KEY`, `SECRET_KEY`, `BUCKET_NAME` 及 `BUCKET_DOMAIN`

    
    QINIU_SETTINGS.Enabled = True    
    
    if QINIU_SETTINGS.Enabled:
        QINIU_SETTINGS.ACCESS_KEY = "ef1ZZEwlvUzY-kBsp0jtWOf2rka0c_q8fnKMG8KP"
        QINIU_SETTINGS.SECRET_KEY = "XMM0GVgToJ3hhmVp9Vm-TDClfUe_IWOanqYSoM3a"
    
        QINIU_SETTINGS.BUCKET_NAME = "me-deepgully"
        QINIU_SETTINGS.BUCKET_DOMAIN = "me-deepgully.qiniudn.com"
        