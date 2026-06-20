# MathLoop Junior 数环错题系统

MathLoop Junior 是一个面向初中生的数学错题闭环训练系统。

核心闭环：

```text
上传错题照片 -> AI 识别 -> 错题卡 -> 同类题 -> 复习计划 -> 今日复习
```

## 技术架构

- 前端：Next.js + React + TypeScript + Tailwind CSS
- 后端：FastAPI + SQLAlchemy + Alembic
- 数据库：PostgreSQL
- 认证：账号密码 + JWT
- 图片：本地开发 uploads，生产支持 S3 兼容对象存储
- 移动端：PWA，可添加到手机主屏幕

## 项目结构

```text
backend/    FastAPI 后端
frontend/   Next.js 前端
docker-compose.yml
README_DEPLOY.md
README_PWA.md
```

## 本地开发

后端：

```bash
cd backend
cp .env.example .env
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

前端：

```bash
cd frontend
cp .env.example .env.local
npm install
npm run dev
```

访问：

```text
http://localhost:3000
```

完整部署说明见：[README_DEPLOY.md](README_DEPLOY.md)

一步一步上线清单见：[DEPLOY_EXECUTION_CHECKLIST.md](DEPLOY_EXECUTION_CHECKLIST.md)

手机安装说明见：[README_PWA.md](README_PWA.md)
