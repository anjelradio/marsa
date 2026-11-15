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
import { EarthScene } from "@/features/landing/presentation/components/earth-scene";
import { useTranslation } from "@/i18n/context";
import { ArrowLeft } from "lucide-react";
import { cn } from "@/lib/utils";
import stars from "@/app/home/starfield.module.css";
import styles from "@/app/landing.module.css";

export default function LoginPage() {
  const { dict } = useTranslation();

  return (
    <div className={cn(styles.landing, "relative isolate flex min-h-svh flex-col items-center justify-center gap-6 overflow-hidden bg-[#050505] p-6 text-white md:p-10 select-none")}>
      {/* Background Live Earth Scene & Orbiting Moon */}
      <div aria-hidden="true" className={styles.sky}>
        <div className={cn(stars.distantStars, "absolute -inset-8 opacity-30")} />
        <div className={cn(stars.nearStars, "absolute -inset-8 opacity-40")} />
        <div className={styles.skyOrbit} />
      </div>
      <div aria-hidden="true" className={cn(styles.scene, "opacity-70 pointer-events-none")}>
        <EarthScene />
      </div>

      {/* Top utility row */}
      <div className="absolute top-4 inset-x-4 sm:inset-x-8 z-20 flex items-center justify-between">
        <Link
          href="/"
          className="flex items-center gap-1.5 text-xs font-medium text-white/80 hover:text-white transition-colors"
        >
          <ArrowLeft className="size-3.5" />
          <span>{dict.common.appName}</span>
        </Link>
        <LanguageSwitcher variant="outline" size="sm" className="border-white/15 bg-white/5 text-white backdrop-blur-md rounded-full" />
      </div>

      <Suspense fallback={null}>
        <AuthErrorNotifier />
      </Suspense>

      {/* Glassmorphic Login Card */}
      <div className="relative z-10 w-full max-w-sm rounded-3xl border border-white/20 bg-black/60 p-6 shadow-2xl backdrop-blur-xl">
        <div className="flex flex-col items-center gap-2 text-center mb-6">
          <HeaderText
            title={dict.auth.login.title}
            description={dict.auth.login.description}
          />
          <FieldDescription className="text-white/70">
            {dict.auth.login.noAccount}{" "}
            <AuthLink href="/auth/signup" label={dict.auth.login.signUpLink} />
          </FieldDescription>
        </div>

        <FieldGroup>
          <LoginForm />
          <FieldSeparator className="text-white/60">{dict.auth.login.orContinueWith}</FieldSeparator>
          <SocialSignInButtons />
        </FieldGroup>
      </div>
    </div>
  );
}
