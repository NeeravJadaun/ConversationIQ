import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "ConversationIQ",
  description: "Real-time operating procedure gap detector for banking AI agents",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
