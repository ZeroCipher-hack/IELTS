import type { Metadata } from "next";
import { Plus_Jakarta_Sans } from "next/font/google";
import "./globals.css";
import { ProductProvider } from "@/components/product/product-context";

const jakarta = Plus_Jakarta_Sans({
  subsets: ["latin"],
  weight: ["500", "600", "700", "800"],
  variable: "--font-jakarta",
  display: "swap",
});

export const metadata: Metadata = {
  title: "IELTSQA — Natijangiz, keyingi qadamingiz",
  description: "IELTS Academic sinov imtihoni platformasi. Natijalar, xatolar tahlili va shaxsiy haftalik reja.",
  icons: {
    icon: "/favicon.svg",
    shortcut: "/favicon.svg",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="uz" suppressHydrationWarning className={jakarta.variable}>
      <body className="antialiased"><script dangerouslySetInnerHTML={{__html: `(function(){try{var t=localStorage.getItem('ieltsqa-theme-v1');document.documentElement.dataset.theme=t==='dark'||(t!=='light'&&matchMedia('(prefers-color-scheme: dark)').matches)?'dark':'light'}catch(e){document.documentElement.dataset.theme='light'}})()`}}/><ProductProvider>{children}</ProductProvider></body>
    </html>
  );
}
