# MathLoop Junior V1.0 上线执行清单

这份清单按“先准备云资源，再部署后端，再部署前端，最后绑定域名和测试”的顺序执行。

建议正式域名：

- 前端：`https://mathloop.your-domain.com`
- 后端：`https://api.mathloop.your-domain.com`
- 图片 CDN：`https://img.mathloop.your-domain.com`

下面示例里的域名、密码、密钥都要替换成你自己的真实值。

## 0. 上线前准备

准备账号：

- GitHub：代码仓库
- Vercel：部署前端
- Render：部署后端和 PostgreSQL
- Cloudflare：DNS 和 R2 图片存储

准备这些值，后面会用到：

```text
FRONTEND_URL=https://mathloop.your-domain.com
BACKEND_URL=https://api.mathloop.your-domain.com
IMAGE_CDN_URL=https://img.mathloop.your-domain.com
JWT_SECRET_KEY=一串至少 32 位的随机字符串
```

生成 `JWT_SECRET_KEY`：

```bash
openssl rand -hex 32
```

## 1. Vercel 前端部署步骤

### 1.1 导入项目

1. 打开 Vercel。
2. 点击右上角 `Add New...`。
3. 选择 `Project`。
4. 选择 GitHub 中的 `mathloop-junior` 仓库。
5. 点击 `Import`。

### 1.2 配置项目目录和构建命令

在 Vercel 的项目配置页填写：

```text
Framework Preset: Next.js
Root Directory: frontend
Build Command: pnpm build
Install Command: pnpm install --frozen-lockfile
Output Directory: 留空
```

如果 Vercel 自动识别为 Next.js，只需要确认 `Root Directory` 是 `frontend`。

### 1.3 配置前端环境变量

进入：

```text
Vercel 项目 -> Settings -> Environment Variables
```

添加：

```text
NEXT_PUBLIC_API_BASE_URL=https://api.mathloop.your-domain.com
NEXT_PUBLIC_APP_NAME=MathLoop Junior
```

环境选择：

```text
Production: 勾选
Preview: 可选
Development: 可选
```

### 1.4 部署前端

1. 点击 `Deploy`。
2. 等待构建完成。
3. 打开 Vercel 给出的临时域名，例如：

```text
https://mathloop-junior-xxx.vercel.app
```

### 1.5 验证成功

打开 Vercel 临时域名，应该看到：

- 能进入登录页。
- 打开注册页不报错。
- 页面没有空白。

此时后端还没部署，登录注册可能暂时无法成功，这是正常的。

## 2. Render 后端部署步骤

### 2.1 新建后端 Web Service

1. 打开 Render。
2. 点击 `New +`。
3. 选择 `Web Service`。
4. 连接 GitHub 仓库。
5. 选择 `mathloop-junior` 仓库。

### 2.2 填写后端服务配置

填写：

```text
Name: mathloop-junior-api
Runtime: Python
Root Directory: backend
Branch: main
Region: Singapore 或离你最近的区域
Build Command: pip install -r requirements.txt
Start Command: alembic upgrade head && gunicorn app.main:app -k uvicorn.workers.UvicornWorker -b 0.0.0.0:$PORT
```

实例规格：

```text
Starter / Basic 均可
```

如果只是家里孩子使用，先用最低付费规格即可。免费规格可能休眠，第一次打开会慢。

### 2.3 暂不启动，先配置环境变量

进入：

```text
Render Web Service -> Environment
```

添加：

```text
ENVIRONMENT=production
DATABASE_URL=Render PostgreSQL 提供的 External Database URL，建议改成 postgresql+psycopg:// 开头
JWT_SECRET_KEY=你用 openssl 生成的 32 位以上随机字符串
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080
CORS_ORIGINS=https://mathloop.your-domain.com,https://你的-vercel-临时域名.vercel.app
STORAGE_MODE=s3
MAX_UPLOAD_MB=10
AI_MODE=mock
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4o-mini
GEMINI_API_KEY=
GEMINI_MODEL=
S3_ENDPOINT_URL=https://你的-r2-account-id.r2.cloudflarestorage.com
S3_ACCESS_KEY_ID=Cloudflare R2 Access Key ID
S3_SECRET_ACCESS_KEY=Cloudflare R2 Secret Access Key
S3_BUCKET_NAME=mathloop-junior
S3_PUBLIC_BASE_URL=https://img.mathloop.your-domain.com
S3_REGION=auto
```

重要：

- `DATABASE_URL` 必须是 PostgreSQL。
- `JWT_SECRET_KEY` 不能使用示例值。
- `CORS_ORIGINS` 必须包含正式前端域名和 Vercel 临时域名。
- `STORAGE_MODE` 上线建议使用 `s3`。

### 2.4 部署后端

1. 保存环境变量。
2. 点击 `Manual Deploy`。
3. 选择 `Deploy latest commit`。
4. 等待构建和启动完成。

### 2.5 验证成功

打开：

```text
https://你的-render-api域名.onrender.com/health
```

应该返回：

```json
{"ok":true,"version":"1.0.0"}
```

如果返回 500：

- 检查 `JWT_SECRET_KEY` 是否还是默认值。
- 检查 `DATABASE_URL` 是否正确。
- 检查 Render 日志里 Alembic 是否迁移失败。

## 3. PostgreSQL 配置步骤

### 3.1 在 Render 创建 PostgreSQL

1. 打开 Render。
2. 点击 `New +`。
3. 选择 `PostgreSQL`。
4. 填写：

```text
Name: mathloop-junior-db
Database: mathloop
User: mathloop
Region: 和后端 Web Service 一致
Plan: Starter 或最低可用付费方案
```

5. 点击创建。

### 3.2 复制数据库连接串

进入：

```text
Render PostgreSQL -> Info
```

复制：

```text
External Database URL
```

Render 常见格式类似：

```text
postgresql://user:password@host/database
```

本项目建议改成：

```text
postgresql+psycopg://user:password@host/database
```

把改好的值填入后端环境变量：

```text
DATABASE_URL=postgresql+psycopg://user:password@host/database
```

### 3.3 验证数据库初始化

后端第一次启动时会自动执行：

```bash
alembic upgrade head
```

验证方式：

1. 打开 Render 后端日志。
2. 搜索 `alembic upgrade head`。
3. 没有报错即可。
4. 再打开 `/health`，返回 `ok: true`。

如果迁移失败：

- 确认数据库服务已经创建完成。
- 确认 `DATABASE_URL` 没有复制错。
- 确认连接串使用 `postgresql+psycopg://`。

## 4. Cloudflare R2 图片存储配置步骤

### 4.1 创建 R2 Bucket

1. 打开 Cloudflare Dashboard。
2. 左侧进入 `R2 Object Storage`。
3. 点击 `Create bucket`。
4. 填写：

```text
Bucket name: mathloop-junior
Location: Automatic
```

5. 点击创建。

### 4.2 创建 R2 API Token

1. 进入 `R2 Object Storage`。
2. 找到 `Manage R2 API Tokens`。
3. 点击 `Create API token`。
4. 权限选择：

```text
Permissions: Object Read & Write
Bucket: mathloop-junior
```

5. 创建后复制：

```text
Access Key ID
Secret Access Key
```

注意：`Secret Access Key` 只显示一次，要马上保存到密码管理器。

### 4.3 获取 R2 S3 Endpoint

在 R2 页面找到你的 Account ID，然后拼出：

```text
S3_ENDPOINT_URL=https://你的-account-id.r2.cloudflarestorage.com
```

例如：

```text
S3_ENDPOINT_URL=https://abc123.r2.cloudflarestorage.com
```

### 4.4 绑定图片公开域名

建议使用：

```text
img.mathloop.your-domain.com
```

在 Cloudflare R2 Bucket 中：

1. 进入 `mathloop-junior` bucket。
2. 找到 `Settings`。
3. 找到 `Public access` 或 `Custom Domains`。
4. 添加自定义域名：

```text
img.mathloop.your-domain.com
```

5. 按 Cloudflare 提示完成 DNS 绑定。

### 4.5 在 Render 后端填写 R2 环境变量

Render 后端服务环境变量填写：

```text
STORAGE_MODE=s3
S3_ENDPOINT_URL=https://你的-account-id.r2.cloudflarestorage.com
S3_ACCESS_KEY_ID=你的 Access Key ID
S3_SECRET_ACCESS_KEY=你的 Secret Access Key
S3_BUCKET_NAME=mathloop-junior
S3_PUBLIC_BASE_URL=https://img.mathloop.your-domain.com
S3_REGION=auto
```

保存后重新部署后端。

### 4.6 验证成功

上线后上传一张错题图片。

成功表现：

- 上传接口不报错。
- 错题详情页能看到原图。
- Cloudflare R2 bucket 里出现类似路径：

```text
users/用户ID/mistakes/图片ID.png
```

## 5. 域名绑定步骤

### 5.1 绑定前端域名到 Vercel

在 Vercel：

1. 进入项目。
2. 点击 `Settings`。
3. 点击 `Domains`。
4. 输入：

```text
mathloop.your-domain.com
```

5. 点击 `Add`。
6. 按 Vercel 提示去 Cloudflare DNS 添加记录。

常见 DNS 记录：

```text
Type: CNAME
Name: mathloop
Target: cname.vercel-dns.com
Proxy status: DNS only 或按 Vercel 提示
```

验证成功：

- Vercel Domains 页面显示 `Valid Configuration`。
- 打开 `https://mathloop.your-domain.com` 能进入登录页。

### 5.2 绑定后端域名到 Render

在 Render 后端 Web Service：

1. 进入 `Settings`。
2. 找到 `Custom Domains`。
3. 添加：

```text
api.mathloop.your-domain.com
```

4. 按 Render 提示去 Cloudflare DNS 添加记录。

常见 DNS 记录：

```text
Type: CNAME
Name: api.mathloop
Target: Render 提供的地址
Proxy status: DNS only
```

验证成功：

```text
https://api.mathloop.your-domain.com/health
```

返回：

```json
{"ok":true,"version":"1.0.0"}
```

### 5.3 更新环境变量中的正式域名

Vercel 前端环境变量：

```text
NEXT_PUBLIC_API_BASE_URL=https://api.mathloop.your-domain.com
NEXT_PUBLIC_APP_NAME=MathLoop Junior
```

Render 后端环境变量：

```text
CORS_ORIGINS=https://mathloop.your-domain.com
S3_PUBLIC_BASE_URL=https://img.mathloop.your-domain.com
```

如果还要保留 Vercel 临时域名测试：

```text
CORS_ORIGINS=https://mathloop.your-domain.com,https://你的-vercel-临时域名.vercel.app
```

修改后：

1. Vercel 重新部署前端。
2. Render 重新部署后端。

## 6. 上线后测试步骤

### 6.1 基础健康检查

打开：

```text
https://api.mathloop.your-domain.com/health
```

成功结果：

```json
{"ok":true,"version":"1.0.0"}
```

打开：

```text
https://mathloop.your-domain.com
```

成功结果：

- 能看到登录页或 Dashboard。
- 页面没有空白。
- 浏览器控制台没有 API 域名错误。

### 6.2 注册账号

1. 打开前端正式域名。
2. 点击注册。
3. 填写：

```text
家长姓名: 你的名字
邮箱: 你的常用邮箱
密码: 至少 6 位
```

4. 点击注册。

成功结果：

- 自动登录或跳转到 Dashboard。
- Dashboard 能打开。

### 6.3 登录账号

1. 退出登录。
2. 使用刚才的邮箱和密码登录。

成功结果：

- 能进入 Dashboard。
- 刷新页面后仍保持登录。

### 6.4 上传错题图片

1. 点击底部或侧边栏「上传」。
2. 点击「拍照或选择图片」。
3. 选择一张真实错题照片。
4. 点击「开始识别」。
5. 等 AI mock 返回结果后，检查内容。
6. 点击「生成错题卡」。

成功结果：

- 自动进入错题详情页。
- 页面显示原图。
- 页面显示题目、答案、解析、错因、知识点和同类题。

### 6.5 检查图片是否进入 R2

打开 Cloudflare：

```text
R2 Object Storage -> mathloop-junior bucket
```

成功结果：

看到类似文件：

```text
users/用户ID/mistakes/xxxx.png
```

再打开错题详情页，图片能正常显示。

### 6.6 查看错题库

1. 点击「错题库」。
2. 查找刚上传的错题。
3. 点击进入详情。

成功结果：

- 错题列表能看到新错题。
- 筛选和搜索不会报错。
- 详情页能打开。

### 6.7 今日复习

1. 点击「今日复习」。
2. 找到刚生成的错题。
3. 点击「答对了」或「还没掌握」。

成功结果：

- 提交后页面刷新。
- Dashboard 中待复习数量会变化。
- 错题详情里的复习状态会更新。

### 6.8 Dashboard 检查

1. 回到 Dashboard。
2. 查看：

```text
错题总数
本周新增
今日待复习
高频错题
薄弱知识点
主要错因
```

成功结果：

- 数字不是空白。
- 上传和复习后数据有变化。

### 6.9 手机安装 PWA

iPhone：

1. 用 Safari 打开 `https://mathloop.your-domain.com`。
2. 点击分享按钮。
3. 点击「添加到主屏幕」。
4. 从桌面图标打开。

Android：

1. 用 Chrome 打开 `https://mathloop.your-domain.com`。
2. 点击浏览器菜单。
3. 选择「安装应用」或「添加到主屏幕」。
4. 从桌面图标打开。

成功结果：

- 能像 App 一样打开。
- 登录、上传、错题库、复习都能使用。

## 7. 最终上线检查

- [ ] Vercel 前端已部署成功。
- [ ] Render 后端 `/health` 正常。
- [ ] Render PostgreSQL 已连接。
- [ ] 后端日志没有迁移错误。
- [ ] Cloudflare R2 bucket 已创建。
- [ ] R2 Access Key 已填入 Render。
- [ ] 图片上传后能在 R2 看到文件。
- [ ] 前端正式域名已绑定。
- [ ] 后端正式域名已绑定。
- [ ] `NEXT_PUBLIC_API_BASE_URL` 是后端 HTTPS 正式域名。
- [ ] `CORS_ORIGINS` 包含前端 HTTPS 正式域名。
- [ ] `JWT_SECRET_KEY` 已换成强随机字符串。
- [ ] `ENVIRONMENT=production`。
- [ ] `STORAGE_MODE=s3`。
- [ ] 注册成功。
- [ ] 登录成功。
- [ ] 上传错题成功。
- [ ] AI mock 分析成功。
- [ ] 错题卡生成成功。
- [ ] 错题库显示成功。
- [ ] 今日复习提交成功。
- [ ] Dashboard 数据正常。
- [ ] 手机 PWA 可添加到主屏幕。
