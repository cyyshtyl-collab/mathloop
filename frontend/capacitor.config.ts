import type { CapacitorConfig } from "@capacitor/cli";

const config: CapacitorConfig = {
  appId: "com.mathloop.junior",
  appName: "MathLoop Junior",
  webDir: "out",
  server: {
    androidScheme: "https"
  }
};

export default config;
