# Render 部署指南 — AI驱动的A股数据分析平台

## 为什么选 Render？
- 免费，无需信用卡
- 支持 Python
- 自动从 GitHub 部署
- 给一个公网网址，任何地方都能打开

---

## 第一步：注册账号（5分钟）

1. 注册 GitHub：https://github.com/signup
2. 注册 Render：https://render.com （点 **Sign Up**，用 GitHub 账号登录）

---

## 第二步：把代码传到 GitHub

### 方法A：用GitHub网页上传（最简单）

1. 打开 https://github.com/new
2. 仓库名填 `a-stock-analyzer`，选 **Public**，点 Create repository
3. 进入仓库后点 **uploading an existing file**
4. 把 `C:\Users\dh124\成果` 文件夹里的**所有文件**拖进去
5. 点 **Commit changes**

### 方法B：用命令行

```bash
cd C:\Users\dh124\成果
git init
git add .
git commit -m "init"
git branch -M main
git remote add origin https://github.com/你的用户名/a-stock-analyzer.git
git push -u origin main
```

---

## 第三步：在 Render 上部署（3分钟）

1. 登录 https://dashboard.render.com
2. 点 **New → Web Service**
3. 点 **Configure** 你的 `a-stock-analyzer` 仓库
4. 填表：

```
Name:           a-stock-analyzer
Region:         Singapore
Branch:         main
Runtime:        Python 3
Build Command:  pip install -r requirements.txt
Start Command:  uvicorn main:app --host 0.0.0.0 --port $PORT
```

5. Instance Type 选 **Free**
6. 点 **Create Web Service**

---

## 第四步：获取网址

部署过程大约 3-5 分钟，看日志显示 `Build successful` 和 `Starting service` 就好了。

页面顶部会显示你的网址，类似：
```
https://a-stock-analyzer.onrender.com
```

直接在浏览器打开就能用。

---

## 注意事项

### 1. 免费版休眠
- 15分钟无请求会自动休眠
- 首次打开会等 30 秒左右（冷启动）
- 之后访问就正常了

### 2. 数据源
- akshare 在 Render 上理论上可以拉取腾讯财经数据
- 如果遇到限流，回测和K线图可能暂时加载失败，刷新重试即可

### 3. 端口配置
- 不要改端口，Render 会自动注入 `$PORT` 环境变量
- 代码里已经用 `host="0.0.0.0"` 监听所有网卡

### 4. 更新代码
- 以后在 GitHub 改了代码，Render 会**自动重新部署**
- 不需要手动操作

---

## 常见问题

**Q: 部署失败，日志显示 akshare 安装失败？**
A: requirements.txt 已锁定兼容版本，重新部署一次即可。

**Q: 网址打不开，显示 Service Unavailable？**
A: 免费版在休眠，等 30 秒刷新即可。可以用 [uptimerobot.com](https://uptimerobot.com) 设置每5分钟访问一次防止休眠。

**Q: 想换名字/域名？**
A: Render 免费版只能用 `xxx.onrender.com` 子域名。想绑自己的域名需要付费版。

**Q: 数据加载慢/失败？**
A: akshare 访问的是国内数据源，Render 在海外可能延迟高或被限流。这是正常现象，不影响项目本身的技术展示。

---

## 防止休眠（可选）

用 UptimeRobot 免费监控：
1. 注册 https://uptimerobot.com
2. 点 **Add New Monitor**
3. Monitor Type 选 **HTTP(s)**
4. URL 填你的 Render 网址
5. Monitoring Interval 选 **5 minutes**
6. 点 **Create Monitor**

这样 Render 就不会休眠了。
