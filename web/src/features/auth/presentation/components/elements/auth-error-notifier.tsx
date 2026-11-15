"use client";

import { useEffect } from "react";
import { useSearchParams } from "next/navigation";
import { appToast } from "@/features/shared/presentation/components/notifications/toast";
import { useTranslation } from "@/i18n/context";

/**
 * Component that reads error query params from URL on mount
 * and triggers the corresponding toast.
 */
export default function AuthErrorNotifier() {
  const searchParams = useSearchParams();
  const { dict } = useTranslation();

  useEffect(() => {
    const error = searchParams.get("error");
    if (!error) return;

    const message =
      error === "social"
        ? dict.auth.notifier.socialError
        : dict.auth.notifier.defaultError;

    appToast.error(dict.auth.notifier.title, message);
  }, [searchParams, dict]);

  return null;
}
