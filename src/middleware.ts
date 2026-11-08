import { resolveLocale } from './i18n/index';

export const onRequest = async (context, next) => {
  context.locals.locale = resolveLocale(context.request);
  const response = await next();
  response.headers.set('Content-Language', String(context.locals.locale));
  const contentType = response.headers.get('content-type') ?? '';
  if (contentType.includes('text/html')) {
    response.headers.set('Cache-Control', 'no-store');
  }
  return response;
};
