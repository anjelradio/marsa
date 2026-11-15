export type SupportedLocale = "en" | "es";

export interface LanguageOption {
  code: SupportedLocale;
  name: string;
  flag: string;
}

export const SUPPORTED_LANGUAGES: LanguageOption[] = [
  { code: "en", name: "English", flag: "🇺🇸" },
];

export const DEFAULT_LOCALE: SupportedLocale = "en";
