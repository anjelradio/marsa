"use client";

import { useRef } from "react";
import { cn } from "@/lib/utils";
import { FieldGroup } from "@/components/ui/field";
import TextFormField from "@/features/shared/presentation/components/forms/text-form-field";
import { appToast } from "@/features/shared/presentation/components/notifications/toast";
import SubmitButton from "@/features/shared/presentation/components/custom-buttons/submit-button";
import { useTranslation } from "@/i18n/context";

export function SignupForm({
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
            id="name"
            name="name"
            label={dict.auth.signup.nameLabel}
            placeholder={dict.auth.signup.namePlaceholder}
            type="text"
            autoComplete="name"
          />
          <TextFormField
            id="email"
            name="email"
            label={dict.auth.signup.emailLabel}
            placeholder={dict.auth.signup.emailPlaceholder}
            type="email"
            autoComplete="email"
          />
          <TextFormField
            id="password"
            name="password"
            label={dict.auth.signup.passwordLabel}
            placeholder={dict.auth.signup.passwordPlaceholder}
            type="password"
            autoComplete="new-password"
          />
          <SubmitButton
            text={dict.auth.signup.submitButton}
            pendingText={dict.auth.signup.submittingButton}
          />
        </FieldGroup>
      </form>
    </div>
  );
}
