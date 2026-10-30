import type { Metadata, Viewport } from "next";
import localFont from "next/font/local";
import "@rainbow-me/rainbowkit/styles.css";
import "./globals.css";
import Providers from "@/components/Providers";
import Header from "@/components/Header";
import Footer from "@/components/Footer";
import { site } from "@/lib/site";

const fraunces = localFont({ src: [{ path: "../fonts/Fraunces_700Bold.ttf", weight: "700" }, { path: "../fonts/Fraunces_900Black.ttf", weight: "900" }], variable: "--font-fraunces" });
const dmsans = localFont({ src: [{ path: "../fonts/DMSans_400Regular.ttf", weight: "400" }, { path: "../fonts/DMSans_500Medium.ttf", weight: "500" }, { path: "../fonts/DMSans_700Bold.ttf", weight: "700" }], variable: "--font-dmsans" });
const caveat = localFont({ src: [{ path: "../fonts/Caveat_700Bold.ttf", weight: "700" }], variable: "--font-caveat" });

export const metadata: Metadata = {
  metadataBase: new URL(site.url),
  title: { default: `${site.collection} — ${site.brand}`, template: `%s · ${site.brand}` },
  description: `${site.collection}: 10,000 wonderfully weird characters. ${site.message}`,
  openGraph: { title: `${site.collection} — ${site.brand}`, description: site.slogan, images: ["/brand/og.png"] },
  twitter: { card: "summary_large_image" },
  icons: { icon: "/brand/favicon.svg" },
};
export const viewport: Viewport = { themeColor: "#141a2e" };

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${fraunces.variable} ${dmsans.variable} ${caveat.variable}`}>
      <body className="min-h-screen flex flex-col">
        <Providers>
          <Header />
          <main className="flex-1">{children}</main>
          <Footer />
        </Providers>
      </body>
    </html>
  );
}
