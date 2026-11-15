"use client";

import Link from "next/link";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { LanguageSwitcher } from "@/features/shared/presentation/components/language-switcher";
import { useTranslation } from "@/i18n/context";
import { ArrowLeft } from "lucide-react";

export default function VerificationPage() {
  const { dict } = useTranslation();

  return (
    <div className="relative flex min-h-svh flex-col items-center justify-center bg-background p-6">
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

      <Card className="w-full max-w-md text-center">
        <CardHeader>
          <div className="mx-auto mb-2 flex size-14 items-center justify-center rounded-full bg-primary/10 text-3xl">
            ✉️
          </div>
          <CardTitle className="text-xl">{dict.auth.verifyEmail.title}</CardTitle>
          <CardDescription>
            {dict.auth.verifyEmail.description}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">
            {dict.auth.verifyEmail.spamNotice}
          </p>
        </CardContent>
        <CardFooter className="justify-center">
          <Button variant="outline" size="sm" asChild>
            <Link href="/auth/login">{dict.auth.verifyEmail.backToLogin}</Link>
          </Button>
        </CardFooter>
      </Card>
    </div>
  );
}
