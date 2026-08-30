import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";

import "./globals.css";
import { QueryProvider } from "@/components/providers/query-provider";
import { AppToaster } from "@/components/shared/app-toaster";
import { AppNavigation } from "@/components/shared/moderation/app-navigation";
import { ClearStorageButton } from "@/components/shared/moderation/clear-storage-button";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Gardien de Contenu IA — Modération de contenu",
  description:
    "Assistant de modération de contenu avec audit de biais et explicabilité.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html
      lang="fr"
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}
    >
      <body className="min-h-full flex flex-col bg-background text-foreground">
        <QueryProvider>
          <AppNavigation />
          <main className="flex-1 app-section">{children}</main>
          <ClearStorageButton />
          <AppToaster position="bottom-right" />
        </QueryProvider>
      </body>
    </html>
  );
}
