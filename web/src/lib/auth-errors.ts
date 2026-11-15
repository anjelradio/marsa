/**
 * Error message mapping for Better Auth codes in both English (default) and Spanish.
 */

import { SupportedLocale } from "@/i18n/types";

const ERROR_MESSAGES_EN: Record<string, string> = {
  USER_ALREADY_EXISTS: "An account with this email already exists. Try signing in.",
  FAILED_TO_CREATE_USER: "Could not create your account. Please try again later.",
  FAILED_TO_CREATE_SESSION: "Account created, but we could not sign you in automatically. Please sign in manually.",
  PASSWORD_TOO_SHORT: "Password must be at least 8 characters long.",
  PASSWORD_TOO_LONG: "Password is too long.",
  INVALID_EMAIL: "Email format is not valid.",
  INVALID_EMAIL_OR_PASSWORD: "Incorrect credentials. Please verify your email and password.",
  EMAIL_NOT_VERIFIED: "You must verify your email before continuing. Please check your inbox.",
  USER_NOT_FOUND: "No account found with that email address.",
  SESSION_EXPIRED: "Your session has expired. Please sign in again.",
  INVALID_TOKEN: "The link is invalid or has already been used. Please request a new one.",
  TOKEN_EXPIRED: "The link has expired. Request a new one via 'Forgot your password?'.",
  ACCOUNT_NOT_LINKED: "This account was created with email and password. Sign in using those credentials.",
  SOCIAL_ACCOUNT_ALREADY_LINKED: "This Google account is already linked to another user.",
  FAILED_TO_GET_USER_INFO: "Could not retrieve user info from provider. Please try again.",
  PROVIDER_NOT_FOUND: "This sign-in method is unavailable.",
  CROSS_SITE_NAVIGATION_LOGIN_BLOCKED: "Sign in was blocked by browser cross-site navigation. Please try again.",
};

const ERROR_MESSAGES_ES: Record<string, string> = {
  USER_ALREADY_EXISTS: "Ya existe una cuenta con este email. Intenta iniciar sesión.",
  FAILED_TO_CREATE_USER: "No pudimos crear tu cuenta. Inténtalo de nuevo más tarde.",
  FAILED_TO_CREATE_SESSION: "Cuenta creada, pero no pudimos iniciar sesión. Intenta entrar manualmente.",
  PASSWORD_TOO_SHORT: "La contraseña debe tener al menos 8 caracteres.",
  PASSWORD_TOO_LONG: "La contraseña es demasiado larga.",
  INVALID_EMAIL: "El formato del email no es válido.",
  INVALID_EMAIL_OR_PASSWORD: "Credenciales incorrectas. Revisa tu email y contraseña.",
  EMAIL_NOT_VERIFIED: "Debes verificar tu email antes de continuar. Revisa tu bandeja de entrada.",
  USER_NOT_FOUND: "No encontramos ninguna cuenta con ese email.",
  SESSION_EXPIRED: "Tu sesión expiró. Inicia sesión de nuevo.",
  INVALID_TOKEN: "El enlace no es válido o ya fue utilizado. Solicita uno nuevo.",
  TOKEN_EXPIRED: "El enlace expiró. Solicita uno nuevo desde '¿Olvidaste tu contraseña?'.",
  ACCOUNT_NOT_LINKED: "Esta cuenta fue creada con email y contraseña. Inicia sesión de esa manera.",
  SOCIAL_ACCOUNT_ALREADY_LINKED: "Esta cuenta de Google ya está asociada a otro usuario.",
  FAILED_TO_GET_USER_INFO: "No pudimos obtener tu información del proveedor. Intenta de nuevo.",
  PROVIDER_NOT_FOUND: "Este método de inicio de sesión no está disponible.",
  CROSS_SITE_NAVIGATION_LOGIN_BLOCKED: "El inicio de sesión fue bloqueado por el navegador. Intenta de nuevo.",
};

export function getAuthErrorMessage(code: string | undefined, locale: SupportedLocale = "en"): string {
  const dict = locale === "es" ? ERROR_MESSAGES_ES : ERROR_MESSAGES_EN;
  const fallback = locale === "es" 
    ? "Ocurrió un error inesperado. Inténtalo de nuevo." 
    : "An unexpected error occurred. Please try again.";

  if (!code) return fallback;
  return dict[code] ?? fallback;
}
