"use client";

import { Suspense } from "react";
import Link from "next/link";
import { LoginForm } from "@/features/auth/presentation/components/forms/login-form";
import {
  FieldDescription,
  FieldGroup,
  FieldSeparator,
} from "@/components/ui/field";
import HeaderText from "@/features/auth/presentation/components/elements/header-text";
import SocialSignInButtons from "@/features/auth/presentation/components/elements/social-sign-in-buttons";
import { AuthLink } from "@/features/auth/presentation/components/elements/auth-link";
import AuthErrorNotifier from "@/features/auth/presentation/components/elements/auth-error-notifier";
import { LanguageSwitcher } from "@/features/shared/presentation/components/language-switcher";
import { useTranslation } from "@/i18n/context";
import { ArrowLeft } from "lucide-react";

export default function LoginPage() {
  const { dict } = useTranslation();

  return (
    <div className="relative flex min-h-svh flex-col items-center justify-center gap-6 bg-background p-6 md:p-10">
      {/* Top utility row */}
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

      <Suspense fallback={null}>
        <AuthErrorNotifier />
      </Suspense>

      <div className="flex flex-col items-center gap-2 text-center">
        <HeaderText
          title={dict.auth.login.title}
          description={dict.auth.login.description}
        />
        <FieldDescription>
          {dict.auth.login.noAccount}{" "}
          <AuthLink href="/auth/signup" label={dict.auth.login.signUpLink} />
        </FieldDescription>
      </div>

      <div className="w-full max-w-sm">
        <FieldGroup>
          <LoginForm />
          <FieldSeparator>{dict.auth.login.orContinueWith}</FieldSeparator>
          <SocialSignInButtons />
        </FieldGroup>
      </div>
    </div>
  );
}
