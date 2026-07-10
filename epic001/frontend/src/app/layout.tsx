import type { Metadata } from "next";
import type { ReactNode } from "react";

import "../shared/styles/globals.css";

export const metadata: Metadata = {
  title: "NextMove",
  description: "AI Career Intelligence",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
