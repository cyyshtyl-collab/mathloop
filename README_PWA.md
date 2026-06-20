# MathLoop Junior PWA 安装说明

MathLoop Junior V1.0 是 PWA，不需要上架 App Store，也可以像 App 一样添加到手机桌面。

## iPhone 安装到桌面

1. 用 Safari 打开你的 MathLoop Junior 前端网址。
2. 登录账号。
3. 点击底部分享按钮。
4. 选择「添加到主屏幕」。
5. 确认名称为 MathLoop，点击添加。

注意：iPhone 必须使用 Safari 才能添加到主屏幕。

## Android 安装到桌面

1. 用 Chrome 打开你的 MathLoop Junior 前端网址。
2. 登录账号。
3. 如果浏览器出现「安装应用」提示，点击安装。
4. 如果没有提示，点击右上角菜单，选择「添加到主屏幕」或「安装应用」。

## Chrome 桌面端安装

1. 用 Chrome 打开网站。
2. 地址栏右侧如果出现安装图标，点击安装。
3. 或在菜单里选择「保存并分享」->「安装页面为应用」。

## Safari 注意事项

- iOS Safari 支持添加到主屏幕，但安装提示不会像 Android Chrome 那样自动弹出。
- 如果无法添加，请确认网站使用 HTTPS。
- 本地开发地址仅用于测试，正式手机安装建议使用 HTTPS 域名。

## PWA 和原生 App 的区别

PWA：

- 不需要上架应用商店
- 更新网页后用户重新打开即可使用新版
- 适合家庭自用和 V1.0 快速上线

原生 App：

- 可以使用更多系统能力
- 需要 iOS / Android 打包和开发者账号
- 上架和审核周期更长

## 后续如何用 Capacitor 打包 iOS / Android

项目已预留 `frontend/capacitor.config.ts`。

后续步骤：

```bash
cd frontend
npm install @capacitor/core @capacitor/cli
npm run build
npx cap init
npx cap add ios
npx cap add android
npx cap sync
```

然后：

- iOS：用 Xcode 打开 `ios/`，配置签名后运行或打包。
- Android：用 Android Studio 打开 `android/`，配置后运行或打包。

V1.0 暂不建议直接做原生 App，先用 PWA 验证家庭真实使用流程。
