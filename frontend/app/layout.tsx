import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "AutoWeb Outreach AI",
  description: "Automated lead generation platform with AI-powered website previews",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
