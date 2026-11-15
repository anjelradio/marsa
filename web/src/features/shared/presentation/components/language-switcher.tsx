"use client";

import { useTranslation } from "@/i18n/context";
import { SupportedLocale } from "@/i18n/types";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Button } from "@/components/ui/button";
import { Globe, Check } from "lucide-react";
import { cn } from "@/lib/utils";

interface LanguageSwitcherProps {
  className?: string;
  variant?: "outline" | "ghost" | "default" | "secondary";
  size?: "default" | "sm" | "lg" | "icon";
  showLabel?: boolean;
}

export function LanguageSwitcher({
  className,
  variant = "ghost",
  size = "sm",
  showLabel = true,
}: LanguageSwitcherProps) {
  const { locale, setLocale, languages } = useTranslation();
  const currentLanguage = languages.find((lang) => lang.code === locale) ?? languages[0];

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button
          variant={variant}
          size={size}
          className={cn(
            "flex items-center gap-2 font-medium transition-colors cursor-pointer",
            className
          )}
          aria-label="Change language"
        >
          <Globe className="size-4 shrink-0 opacity-80" />
          <span className="text-base leading-none">{currentLanguage.flag}</span>
          {showLabel && (
            <span className="text-xs uppercase tracking-wider font-semibold">
              {currentLanguage.code}
            </span>
          )}
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-40 p-1.5 backdrop-blur-md">
        {languages.map((lang) => {
          const isSelected = lang.code === locale;
          return (
            <DropdownMenuItem
              key={lang.code}
              onClick={() => setLocale(lang.code as SupportedLocale)}
              className={cn(
                "flex items-center justify-between px-3 py-2 text-sm cursor-pointer rounded-xl transition-colors",
                isSelected && "font-semibold bg-accent text-accent-foreground"
              )}
            >
              <span className="flex items-center gap-2.5">
                <span className="text-base">{lang.flag}</span>
                <span>{lang.name}</span>
              </span>
              {isSelected && <Check className="size-4 opacity-80" />}
            </DropdownMenuItem>
          );
        })}
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
