import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "VisioSync | Layout-aware engineering intelligence",
  description: "Visual retrieval for complex schematics and technical datasheets.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en"><body>{children}</body></html>;
}
