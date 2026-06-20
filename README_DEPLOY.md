# MathLoop Junior V1.0 部署文档

如果你要按步骤直接上线，优先看：[DEPLOY_EXECUTION_CHECKLIST.md](DEPLOY_EXECUTION_CHECKLIST.md)

## 1. 本地开发启动

启动 PostgreSQL 后端数据库，设置后端环境变量：

```bash
cd backend
cp .env.example .env
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

启动前端：

```bash
cd frontend
cp .env.example .env.local
npm install
npm run dev
```

前端访问 `http://localhost:3000`，后端健康检查 `http://localhost:8000/health`。

## 2. 生产部署方式一：Vercel + Render/Railway + PostgreSQL

适合不想自己维护服务器的人。

前端部署到 Vercel：

1. 在 Vercel 新建项目，选择本代码仓库。
2. Root Directory 设置为 `frontend`。
3. Build Command 保持 `npm run build`。
4. 添加环境变量：

```text
NEXT_PUBLIC_API_BASE_URL=https://你的后端域名
```

后端部署到 Render / Railway：

1. 新建 PostgreSQL 数据库，复制连接串。
2. 新建 Web Service，Root Directory 设置为 `backend`。
3. 安装命令：

```bash
pip install -r requirements.txt
```

4. 启动命令：

```bash
alembic upgrade head && gunicorn app.main:app -k uvicorn.workers.UvicornWorker -b 0.0.0.0:$PORT
```

5. 添加环境变量：

```text
DATABASE_URL=你的 PostgreSQL 连接串，建议使用 postgresql+psycopg:// 开头
ENVIRONMENT=production
JWT_SECRET_KEY=强随机字符串
CORS_ORIGINS=https://你的 Vercel 域名
STORAGE_MODE=s3
```

如果暂时只给自己家里使用，也可以先用 `STORAGE_MODE=local`，但平台重建容器时图片可能丢失；正式长期使用建议用对象存储。

## 3. 生产部署方式二：云服务器 Docker Compose

准备环境变量：

```bash
cp .env.example .env
```

修改根目录 `.env` 后启动。云服务器部署时，至少要把这几项改成真实值：

- `POSTGRES_PASSWORD`
- `JWT_SECRET_KEY`
- `CORS_ORIGINS`
- `NEXT_PUBLIC_API_BASE_URL`
- 如果用对象存储，还要配置全部 `S3_` 变量

然后启动：

```bash
docker compose up -d --build
```

启动后检查：

```bash
docker compose ps
curl http://服务器IP:8000/health
```

服务：

- 前端：`http://服务器IP:3000`
- 后端：`http://服务器IP:8000`
- PostgreSQL：容器内部访问

注意：`NEXT_PUBLIC_API_BASE_URL` 是浏览器里访问后端的地址。云服务器上不能继续使用本机开发地址，要写成你的服务器公网地址或后端域名，例如 `https://api.your-domain.com`。

## 4. 如何配置环境变量

后端关键变量：

- `DATABASE_URL`：PostgreSQL 连接串
- `POSTGRES_USER` / `POSTGRES_PASSWORD` / `POSTGRES_DB`：Docker Compose 内置 PostgreSQL 使用
- `ENVIRONMENT`：生产环境设为 `production`
- `JWT_SECRET_KEY`：强随机字符串
- `CORS_ORIGINS`：前端正式域名
- `STORAGE_MODE`：`local` 或 `s3`
- `AI_MODE`：当前可用 `mock`

前端关键变量：

- `NEXT_PUBLIC_API_BASE_URL`：后端正式地址

## 5. 如何配置对象存储

生产建议：

```text
STORAGE_MODE=s3
S3_ENDPOINT_URL=https://xxx.r2.cloudflarestorage.com
S3_ACCESS_KEY_ID=你的 key
S3_SECRET_ACCESS_KEY=你的 secret
S3_BUCKET_NAME=mathloop
S3_PUBLIC_BASE_URL=https://cdn.your-domain.com
S3_REGION=auto
```

Cloudflare R2、AWS S3、阿里云 OSS、腾讯云 COS 只要兼容 S3 API，都可以使用。

## 6. 如何初始化数据库

首次部署后执行：

```bash
cd backend
alembic upgrade head
```

Docker Compose 会在后端容器启动时自动执行迁移。

## 7. 如何创建第一个账号

打开前端 `/register` 页面，注册家长账号。V1.0 支持自助注册，所有错题数据会绑定到当前登录用户。

## 8. 如何检查服务是否正常

后端：

```bash
curl https://你的后端域名/health
```

返回：

```json
{"ok":true,"version":"1.0.0"}
```

前端：

- 能打开登录页
- 能注册 / 登录
- 能上传图片并生成错题卡

后端完整流程自检：

```bash
cd backend
DATABASE_URL=你的测试数据库连接串 \
UPLOAD_DIR=uploads \
STORAGE_MODE=local \
JWT_SECRET_KEY=测试密钥 \
PYTHONPATH=. \
python scripts/smoke_flow.py
```

看到 `FLOW_OK` 表示注册、登录、上传、AI mock、建卡、复习和 Dashboard 都跑通。

## 9. 如何测试上传错题

1. 打开前端网址。
2. 注册或登录。
3. 进入「上传」。
4. 手机点击「拍照或选择图片」。
5. 拍照或从相册选择错题。
6. 点击「开始识别」。
7. 检查并修改识别结果。
8. 点击「生成错题卡」。
9. 自动进入错题详情页，确认同类题和复习计划。

## 10. 如何测试 PWA 安装

1. 使用 HTTPS 域名打开前端。
2. Android Chrome：菜单中选择「安装应用」或「添加到主屏幕」。
3. iPhone Safari：点击分享按钮，选择「添加到主屏幕」。
4. 从桌面图标打开 MathLoop，确认显示为独立 App 窗口。

更多说明见 [README_PWA.md](README_PWA.md)。

## 11. 如何绑定域名

前端 Vercel：

- 在 Vercel 项目中添加你的前端域名，例如 `mathloop.your-domain.com`。
- 把 DNS CNAME 指向 Vercel 提供的地址。

后端 Render / Railway / 云服务器：

- 配置后端域名，例如 `api.your-domain.com`。
- 确保 HTTPS 可用。
- 把 `NEXT_PUBLIC_API_BASE_URL` 改为后端 HTTPS 地址。
- 把 `CORS_ORIGINS` 改为前端 HTTPS 地址。
## 12. 如何检查 /health

```bash
curl https://你的后端域名/health
```

返回 `{"ok":true,"version":"1.0.0"}` 表示后端正常。

## 13. 常见问题排查

- 登录后接口 401：检查 `JWT_SECRET_KEY` 是否变更，重新登录。
- 前端无法请求后端：检查 `NEXT_PUBLIC_API_BASE_URL` 和 `CORS_ORIGINS`。
- 数据重启丢失：确认使用 PostgreSQL，且 Docker volume 未删除。
- 图片无法显示：检查 `STORAGE_MODE`、S3 public base URL 或本地 uploads 挂载。
- 上传失败：确认图片类型为 jpg / jpeg / png / webp，大小不超过 `MAX_UPLOAD_MB`。

## 上线前检查

- [ ] DATABASE_URL 已配置为 PostgreSQL
- [ ] JWT_SECRET_KEY 已换成强随机字符串
- [ ] CORS_ORIGINS 已配置正式域名
- [ ] NEXT_PUBLIC_API_BASE_URL 已配置后端正式地址
- [ ] STORAGE_MODE 已确认
- [ ] 生产环境对象存储已配置
- [ ] 图片上传测试成功
- [ ] 注册登录测试成功
- [ ] 上传错题测试成功
- [ ] 错题库数据刷新正常
- [ ] 今日复习正常
- [ ] Dashboard 正常
- [ ] 用户 A 无法访问用户 B 数据
- [ ] .env 没有提交到代码仓库
- [ ] /health 返回正常
