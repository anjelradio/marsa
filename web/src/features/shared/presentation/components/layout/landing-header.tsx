"use client";

import Link from "next/link";
import { Button } from "@/components/ui/button";
import { LanguageSwitcher } from "@/features/shared/presentation/components/language-switcher";
import { useTranslation } from "@/i18n/context";
import { Sparkles } from "lucide-react";

export function LandingHeader() {
  const { dict } = useTranslation();

  return (
    <header className="sticky top-0 z-50 w-full border-b border-border/40 bg-background/80 backdrop-blur-lg">
      <div className="mx-auto flex h-16 max-w-5xl items-center justify-between px-6">
        <Link href="/" className="flex items-center gap-1.5 font-headline text-lg font-bold tracking-tight">
          <span>{dict.common.appName}</span>
          <Sparkles className="size-3.5 text-primary" />
        </Link>

        <div className="flex items-center gap-3">
          <LanguageSwitcher variant="ghost" size="sm" />

          <nav className="flex items-center gap-2">
            <Button size="sm" asChild>
              <Link href="/home">Explore</Link>
            </Button>
          </nav>
        </div>
      </div>
    </header>
  );
}
