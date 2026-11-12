import { resolveLocale } from './i18n/index';

export const onRequest = async (context, next) => {
  context.locals.locale = resolveLocale(context.request);
  const response = await next();
  response.headers.set('Content-Language', String(context.locals.locale));
  const contentType = response.headers.get('content-type') ?? '';
  if (contentType.includes('text/html')) {
    response.headers.set('Cache-Control', 'no-store');
    // CSRF double-submit token: the contact form JS reads this cookie and
    // echoes it in the X-CSRF-Token header; the backend compares both.
    if (!context.cookies.get('cf_token')?.value) {
      const bytes = new Uint8Array(16);
      crypto.getRandomValues(bytes);
      context.cookies.set('cf_token', Array.from(bytes, (b) => b.toString(16).padStart(2, '0')).join(''), {
        path: '/',
        httpOnly: false,
        sameSite: 'lax',
        maxAge: 60 * 60 * 24 * 365,
      });
    }
  }
  return response;
};
