import es from './es.json';
import en from './en.json';

export type Locale = 'es' | 'en';

const dictionaries: Record<Locale, Record<string, string>> = { es, en };
export const LOCALE_COOKIE = 'locale';
export const LOCALES: Locale[] = ['es', 'en'];

export function isLocale(value: string | null | undefined): value is Locale {
  return value === 'es' || value === 'en';
}

/** Cookie → Accept-Language → 'en' (es si el sistema es español, resto → inglés). */
export function resolveLocale(request: Request): Locale {
  const cookie = request.headers.get('cookie') ?? '';
  const match = cookie.match(/(?:^|;\s*)locale=(es|en)(?:;|$)/);
  if (match) return match[1] as Locale;

  const accept = (request.headers.get('accept-language') ?? '').toLowerCase();
  if (accept.startsWith('es') || accept.includes(',es') || accept.includes(';es')) return 'es';
  return 'en';
}

export function translate(locale: Locale, key: string, vars?: Record<string, string | number>): string {
  let text = dictionaries[locale][key] ?? dictionaries.es[key] ?? key;
  if (vars) {
    for (const [name, value] of Object.entries(vars)) {
      text = text.replaceAll(`{${name}}`, String(value));
    }
  }
  return text;
}

/** Server-side helper for .astro files: const { locale, t } = useI18n(Astro). */
export function useI18n(astro: { locals: Record<string, unknown>; request: Request }) {
  const raw = astro.locals?.locale;
  const locale: Locale = isLocale(raw as string) ? (raw as Locale) : resolveLocale(astro.request);
  return {
    locale,
    t: (key: string, vars?: Record<string, string | number>) => translate(locale, key, vars),
  };
}

/** Client-side: locale is mirrored on <html lang> by the server. */
export function getLocale(): Locale {
  if (typeof document === 'undefined') return 'es';
  return document.documentElement.lang === 'en' ? 'en' : 'es';
}

export function t(key: string, vars?: Record<string, string | number>): string {
  return translate(getLocale(), key, vars);
}

export function setLocale(locale: Locale): void {
  if (typeof document === 'undefined') return;
  document.cookie = `${LOCALE_COOKIE}=${locale}; path=/; max-age=31536000; samesite=lax`;
  try {
    localStorage.setItem(LOCALE_COOKIE, locale);
  } catch {
    /* ignore */
  }
}
