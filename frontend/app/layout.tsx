import type { Metadata } from "next";
import "./globals.css";

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
    <html lang="uz" suppressHydrationWarning>
      <body className="antialiased"><script dangerouslySetInnerHTML={{__html: `(function(){try{var t=localStorage.getItem('ieltsqa-theme-v2');document.documentElement.dataset.theme=t==='dark'?'dark':'light'}catch(e){document.documentElement.dataset.theme='light'}})()`}}/>{children}</body>
    </html>
  );
}
