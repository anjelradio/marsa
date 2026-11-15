"use client";

import React, {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react";
import {
  DEFAULT_LOCALE,
  SUPPORTED_LANGUAGES,
  type LanguageOption,
  type SupportedLocale,
} from "./types";
import { en, type TranslationDict } from "./locales/en";
import { translations } from "./index";

interface LanguageContextValue {
  locale: SupportedLocale;
  setLocale: (locale: SupportedLocale) => void;
  dict: TranslationDict;
  t: (path: string, fallback?: string) => string;
  languages: LanguageOption[];
}

const LanguageContext = createContext<LanguageContextValue | null>(null);

const STORAGE_KEY = "astroplus_preferred_locale";

export function LanguageProvider({
  children,
  defaultLocale = DEFAULT_LOCALE,
}: {
  children: React.ReactNode;
  defaultLocale?: SupportedLocale;
}) {
  const [locale, setLocaleState] = useState<SupportedLocale>(defaultLocale);

  // Sync with localStorage on client mount (ensure English is default and active)
  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEY, "en");
      document.documentElement.lang = "en";
    } catch {
      // localStorage may not be accessible in some environments
    }
  }, []);

  const setLocale = useCallback((newLocale: SupportedLocale) => {
    setLocaleState(newLocale);
    try {
      localStorage.setItem(STORAGE_KEY, newLocale);
      document.documentElement.lang = newLocale;
    } catch {
      // ignore
    }
  }, []);

  const dict = useMemo(() => {
    return translations[locale] ?? translations[DEFAULT_LOCALE];
  }, [locale]);

  const t = useCallback(
    (path: string, fallback?: string): string => {
      const keys = path.split(".");
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      let current: any = dict;
      for (const k of keys) {
        if (current && typeof current === "object" && k in current) {
          current = current[k];
        } else {
          // Fallback to English if missing
          // eslint-disable-next-line @typescript-eslint/no-explicit-any
          let enCurrent: any = en;
          for (const ek of keys) {
            if (enCurrent && typeof enCurrent === "object" && ek in enCurrent) {
              enCurrent = enCurrent[ek];
            } else {
              return fallback ?? path;
            }
          }
          return typeof enCurrent === "string" ? enCurrent : (fallback ?? path);
        }
      }
      return typeof current === "string" ? current : (fallback ?? path);
    },
    [dict]
  );

  const value = useMemo(
    () => ({
      locale,
      setLocale,
      dict,
      t,
      languages: SUPPORTED_LANGUAGES,
    }),
    [locale, setLocale, dict, t]
  );

  return (
    <LanguageContext.Provider value={value}>
      {children}
    </LanguageContext.Provider>
  );
}

export function useTranslation() {
  const context = useContext(LanguageContext);
  if (!context) {
    // Graceful fallback for non-provider rendering
    return {
      locale: DEFAULT_LOCALE,
      setLocale: () => {},
      dict: en,
      t: (path: string, fallback?: string) => fallback ?? path,
      languages: SUPPORTED_LANGUAGES,
    };
  }
  return context;
}
