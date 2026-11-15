"use client";

import Link from "next/link";
import { LanguageSwitcher } from "@/features/shared/presentation/components/language-switcher";
import { useTranslation } from "@/i18n/context";
import { Sparkles } from "lucide-react";

export function AppHeader() {
  const { dict } = useTranslation();

  return (
    <header className="flex items-center justify-between border-b border-border/40 px-6 py-4">
      <Link href="/home" className="flex items-center gap-1.5 font-headline text-lg font-bold tracking-tight">
        <span>{dict.common.appName}</span>
        <Sparkles className="size-3.5 text-primary" />
      </Link>
      <LanguageSwitcher variant="ghost" size="sm" />
    </header>
  );
}
