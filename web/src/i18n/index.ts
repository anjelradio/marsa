import { en, type TranslationDict } from "./locales/en";
import { es } from "./locales/es";
import { DEFAULT_LOCALE, SUPPORTED_LANGUAGES, type SupportedLocale } from "./types";

export * from "./types";
export * from "./locales/en";

export const translations: Record<SupportedLocale, TranslationDict> = {
  en,
  es,
};

export function getTranslation(locale: SupportedLocale): TranslationDict {
  return translations[locale] ?? translations[DEFAULT_LOCALE];
}
