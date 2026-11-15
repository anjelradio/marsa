import type { Metadata } from "next";
import "@/styles/globals.css";
import { cn } from "@/lib/utils";
import { Toaster } from "sileo";
import { appFontVariables } from "@/styles/fonts";
import { LanguageProvider } from "@/i18n/context";

export const metadata: Metadata = {
  title: "AstroPlus · NASA Exploration & Dashboard",
  description:
    "Next.js web application with shadcn/ui, Three.js 3D space visualization, and Clean Architecture.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className={cn(
        "h-full",
        "antialiased",
        appFontVariables,
        "font-sans",
      )}
    >
      <body className="min-h-full flex flex-col">
        <LanguageProvider defaultLocale="en">
          {children}
          <Toaster position="top-center" theme="light" />
        </LanguageProvider>
      </body>
    </html>
  );
}
