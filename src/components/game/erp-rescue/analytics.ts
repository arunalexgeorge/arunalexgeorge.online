/* ============================================================
   ERP RESCUE — Analytics (privacy-friendly wrapper over GA4 gtag)
   Fails silently if gtag/consent is unavailable.
   ============================================================ */

declare global {
  interface Window { gtag?: (...args: unknown[]) => void; }
}

export function track(event: string, params: Record<string, unknown> = {}): void {
  try {
    window.gtag?.('event', event, { event_category: 'erp_rescue', ...params });
  } catch { /* no-op */ }
}
