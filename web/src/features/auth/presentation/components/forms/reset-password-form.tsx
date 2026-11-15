"use client";

import { useRef } from "react";
import { cn } from "@/lib/utils";
import { FieldGroup } from "@/components/ui/field";
import TextFormField from "@/features/shared/presentation/components/forms/text-form-field";
import { appToast } from "@/features/shared/presentation/components/notifications/toast";
import SubmitButton from "@/features/shared/presentation/components/custom-buttons/submit-button";
import { useTranslation } from "@/i18n/context";

export function ResetPasswordForm({
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
            id="newPassword"
            name="newPassword"
            label={dict.auth.resetPassword.newPasswordLabel}
            placeholder={dict.auth.resetPassword.newPasswordPlaceholder}
            type="password"
            autoComplete="new-password"
          />
          <TextFormField
            id="confirmPassword"
            name="confirmPassword"
            label={dict.auth.resetPassword.confirmPasswordLabel}
            placeholder={dict.auth.resetPassword.confirmPasswordPlaceholder}
            type="password"
            autoComplete="new-password"
          />
          <SubmitButton
            text={dict.auth.resetPassword.submitButton}
            pendingText={dict.auth.resetPassword.submittingButton}
          />
        </FieldGroup>
      </form>
    </div>
  );
}
