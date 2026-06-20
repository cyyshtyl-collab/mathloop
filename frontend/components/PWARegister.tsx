"use client";

import { useEffect } from "react";

export function PWARegister() {
  useEffect(() => {
    if ("serviceWorker" in navigator) {
      const isLocalhost = ["localhost", "127.0.0.1"].includes(window.location.hostname);
      const canUsePwa = window.location.protocol === "https:" || isLocalhost;
      if (!canUsePwa) {
        navigator.serviceWorker.getRegistrations().then((registrations) => {
          registrations.forEach((registration) => registration.unregister());
        });
        caches?.keys?.().then((keys) => keys.forEach((key) => caches.delete(key)));
        return;
      }
      navigator.serviceWorker.register("/sw.js").catch(() => {});
    }
  }, []);
  return null;
}
