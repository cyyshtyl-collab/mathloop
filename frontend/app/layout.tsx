import type { Metadata, Viewport } from "next";
import { PWARegister } from "@/components/PWARegister";
import "./globals.css";

export const metadata: Metadata = {
  title: "MathLoop Junior 数环错题系统",
  description: "面向初中生的数学错题闭环训练系统",
  manifest: "/manifest.json",
  appleWebApp: {
    capable: true,
    title: "MathLoop",
    statusBarStyle: "default"
  },
  icons: {
    icon: "/icons/icon-192.png",
    apple: "/icons/icon-192.png"
  }
};

export const viewport: Viewport = {
  themeColor: "#2563eb"
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="zh-CN">
      <body>
        <PWARegister />
        {children}
      </body>
    </html>
  );
}
