// Site-wide identity used by page metadata and structured data. Keep these
// facts in step with what the about, resume and contact pages say.
export const SITE_URL = 'https://arunalexgeorge.online';
export const SITE_NAME = 'Arun Alex George';

export const PERSON_ID = `${SITE_URL}/#person`;
export const WEBSITE_ID = `${SITE_URL}/#website`;

export const person = {
  name: 'Arun Alex George',
  jobTitle: 'Senior Odoo Developer & ERP Consultant',
  email: 'hello@arunalexgeorge.online',
  employer: 'Ideenkreise Tech Pvt Ltd',
  locality: 'Kochi',
  region: 'Kerala',
  country: 'IN',
  sameAs: [
    'https://linkedin.com/in/arunageorge',
    'https://github.com/arunalexgeorge',
    'https://medium.com/@arunalexgeorge',
    'https://apps.odoo.com/apps/modules/browse?author=Arun%20A%20George',
  ],
  knowsAbout: [
    'Odoo', 'Odoo development', 'Odoo implementation', 'Odoo migration', 'ERP consulting',
    'Python', 'PostgreSQL', 'Solution architecture', 'Business process automation',
  ],
};

/** Longest title we append the site name to; longer titles stand alone. */
const MAX_TITLE_WITH_BRAND = 65;

export function pageTitle(title: string): string {
  const branded = `${title} — ${SITE_NAME}`;
  return branded.length <= MAX_TITLE_WITH_BRAND ? branded : title;
}

export interface Crumb {
  name: string;
  path: string;
}
