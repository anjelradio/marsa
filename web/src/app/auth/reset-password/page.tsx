"use client";

import { Suspense } from "react";
import Link from "next/link";
import HeaderText from "@/features/auth/presentation/components/elements/header-text";
import { ResetPasswordForm } from "@/features/auth/presentation/components/forms/reset-password-form";
import { LanguageSwitcher } from "@/features/shared/presentation/components/language-switcher";
import { useTranslation } from "@/i18n/context";
import { ArrowLeft } from "lucide-react";

export default function ResetPasswordPage() {
  const { dict } = useTranslation();

  return (
    <div className="relative flex min-h-svh flex-col items-center justify-center gap-6 bg-background p-6 md:p-10">
      {/* Top navigation row */}
      <div className="absolute top-4 inset-x-4 sm:inset-x-8 flex items-center justify-between">
        <Link
          href="/"
          className="flex items-center gap-1.5 text-xs font-medium text-muted-foreground hover:text-foreground transition-colors"
        >
          <ArrowLeft className="size-3.5" />
          <span>{dict.common.appName}</span>
        </Link>
        <LanguageSwitcher variant="outline" size="sm" />
      </div>

      <div className="flex flex-col items-center gap-2 text-center">
        <HeaderText
          title={dict.auth.resetPassword.title}
          description={dict.auth.resetPassword.description}
        />
      </div>
      <div className="w-full max-w-sm">
        <Suspense fallback={null}>
          <ResetPasswordForm />
        </Suspense>
      </div>
    </div>
  );
}
