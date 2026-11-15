"use client";

import { useRef } from "react";
import Link from "next/link";
import { cn } from "@/lib/utils";
import { FieldGroup } from "@/components/ui/field";
import TextFormField from "@/features/shared/presentation/components/forms/text-form-field";
import { appToast } from "@/features/shared/presentation/components/notifications/toast";
import SubmitButton from "@/features/shared/presentation/components/custom-buttons/submit-button";
import { useTranslation } from "@/i18n/context";

export function LoginForm({
  className,
  ...props
}: React.ComponentProps<"div">) {
  const formRef = useRef<HTMLFormElement>(null);
  const { dict } = useTranslation();

  const handleSubmit = async () => {
    appToast.error(
      dict.auth.login.notAvailableTitle,
      dict.auth.login.notAvailableMsg
    );
  };

  return (
    <div className={cn("flex flex-col gap-6", className)} {...props}>
      <form ref={formRef} action={handleSubmit}>
        <FieldGroup>
          <TextFormField
            id="email"
            name="email"
            label={dict.auth.login.emailLabel}
            placeholder={dict.auth.login.emailPlaceholder}
            type="email"
            autoComplete="email"
          />
          <TextFormField
            id="password"
            name="password"
            label={dict.auth.login.passwordLabel}
            placeholder={dict.auth.login.passwordPlaceholder}
            type="password"
            autoComplete="current-password"
          />

          <div className="flex justify-end">
            <Link
              href="/auth/forgot-password"
              className="text-sm text-muted-foreground hover:text-foreground transition-colors"
            >
              {dict.auth.login.forgotPasswordLink}
            </Link>
          </div>

          <SubmitButton
            text={dict.auth.login.submitButton}
            pendingText={dict.auth.login.submittingButton}
          />
        </FieldGroup>
      </form>
    </div>
  );
}
