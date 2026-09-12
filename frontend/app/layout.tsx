import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "IELTSQA — Natijangiz, keyingi qadamingiz",
  description: "IELTS Academic sinov imtihoni platformasi. Natijalar, xatolar tahlili va shaxsiy haftalik reja. Interaktiv demo.",
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
    <html lang="uz">
      <body className="antialiased">{children}</body>
    </html>
  );
}
