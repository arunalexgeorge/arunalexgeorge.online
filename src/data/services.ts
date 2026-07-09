export interface ServiceData {
  slug: string;
  title: string;
  headline: string;
  description: string;
  overview: string;
  benefits: string[];
  process: string[];
  technologies: string[];
  industries: string[];
  faqs: { q: string; a: string }[];
}

export const servicesData: Record<string, ServiceData> = {
  'erp-consulting': {
    slug: 'erp-consulting',
    title: 'ERP Consulting',
    headline: 'Strategic ERP Advisory & Implementation',
    description: 'End-to-end ERP consulting services — from business analysis and system selection to implementation, training, and ongoing support.',
    overview: 'I help businesses choose, implement, and optimize ERP systems that align with their strategic goals. With 20+ successful ERP implementations across diverse industries, I bring deep expertise in Odoo ERP along with a thorough understanding of business processes in manufacturing, retail, healthcare, finance, and more.',
    benefits: ['Streamlined business processes and reduced manual effort', 'Single source of truth across all departments', 'Real-time analytics and reporting for data-driven decisions', 'Scalable systems that grow with your business', 'Reduced operational costs by 30-50%', 'Improved compliance and audit trails'],
    process: ['Discovery & Business Analysis', 'Gap Analysis & Solution Design', 'ERP System Selection & Architecture', 'Implementation Planning & Timeline', 'Configuration & Customization', 'Data Migration & Integration', 'User Training & Change Management', 'Go-Live Support & Optimization'],
    technologies: ['Odoo ERP (v10–v19)', 'Python', 'PostgreSQL', 'REST APIs', 'Docker', 'AWS/DigitalOcean'],
    industries: ['Manufacturing', 'Retail & eCommerce', 'Healthcare & Dental', 'Automobile', 'Real Estate', 'Hospitality', 'Finance & Procurement'],
    faqs: [
      { q: 'How long does a typical ERP implementation take?', a: 'Depending on scope, most implementations take 3-6 months from discovery through go-live. Complex multi-module projects may take longer.' },
      { q: 'Do you work with ERPs other than Odoo?', a: 'I specialize exclusively in Odoo ERP, which allows me to deliver deeper expertise and better outcomes for my clients.' },
      { q: 'What size companies do you work with?', a: 'I work with SMEs, startups, and enterprise clients — from 5-person teams to organizations with 500+ employees.' },
    ],
  },
  'odoo-development': {
    slug: 'odoo-development',
    title: 'Odoo Development',
    headline: 'Custom Odoo Modules & Integrations',
    description: 'Custom Odoo module development, advanced customizations, and seamless third-party integrations tailored to your unique business logic.',
    overview: 'When off-the-shelf Odoo modules don\'t fit your exact workflow, I build custom solutions. From specialized business logic and automated workflows to complex third-party integrations and custom reports, I develop modules that extend Odoo to match your precise requirements.',
    benefits: ['Perfectly tailored to your business workflows', 'Seamless integration with existing Odoo modules', 'Clean, maintainable, upgrade-safe code', 'Comprehensive testing and documentation', 'Ongoing maintenance and version upgrades', 'Published 20+ modules — proven track record'],
    process: ['Requirements Analysis', 'Technical Specification', 'Module Architecture Design', 'Development & Unit Testing', 'Code Review & QA', 'Staging Deployment & UAT', 'Production Deployment', 'Documentation & Handover'],
    technologies: ['Python', 'OWL (Odoo Web Library)', 'PostgreSQL', 'XML/QWeb', 'REST/JSON-RPC APIs', 'JavaScript'],
    industries: ['All industries using Odoo ERP'],
    faqs: [
      { q: 'Will custom modules survive Odoo version upgrades?', a: 'I follow Odoo development best practices and write upgrade-safe code. I also offer migration services when you move to a new Odoo version.' },
      { q: 'Can you integrate Odoo with our existing systems?', a: 'Yes — I build integrations with payment gateways, shipping providers, CRMs, e-commerce platforms, and any system with an API.' },
      { q: 'Do you provide source code ownership?', a: 'Absolutely. You receive full ownership of all custom-developed code with complete documentation.' },
    ],
  },
  'odoo-implementation': {
    slug: 'odoo-implementation',
    title: 'Odoo Implementation',
    headline: 'Full-Cycle Odoo ERP Deployment',
    description: 'Complete Odoo ERP deployment from requirements gathering and configuration through data migration, training, go-live, and post-launch support.',
    overview: 'I provide end-to-end Odoo ERP implementation services, managing every phase from initial discovery through go-live and beyond. My proven 7-step methodology — refined across 20+ implementations — ensures predictable timelines, minimal disruption, and successful adoption.',
    benefits: ['Proven methodology with 20+ successful implementations', 'Minimal business disruption during transition', 'Complete data migration with zero data loss', 'Comprehensive user training for smooth adoption', 'Post-launch monitoring and optimization', 'AMC (Annual Maintenance Contract) for ongoing support'],
    process: ['Discovery & Business Process Mapping', 'Requirements Documentation', 'Solution Design & Configuration', 'Custom Development (if needed)', 'Data Migration & Validation', 'User Acceptance Testing', 'Training & Change Management', 'Go-Live & Post-Launch Support'],
    technologies: ['Odoo ERP (Community & Enterprise)', 'Python', 'PostgreSQL', 'Docker', 'Nginx', 'Linux'],
    industries: ['Manufacturing', 'Retail', 'Healthcare', 'Automobile', 'Real Estate', 'Hospitality', 'Finance'],
    faqs: [
      { q: 'Odoo Community or Enterprise — which should I choose?', a: 'I help you evaluate both options based on your needs and budget. Many businesses start with Community and upgrade later.' },
      { q: 'Can you migrate from our existing ERP?', a: 'Yes. I handle data migration from legacy ERPs, spreadsheets, and other systems into Odoo with complete validation.' },
      { q: 'What happens after go-live?', a: 'I offer Annual Maintenance Contracts (AMC) covering bug fixes, minor enhancements, server monitoring, and Odoo version upgrades.' },
    ],
  },
  'odoo-customization': {
    slug: 'odoo-customization',
    title: 'Odoo Customization',
    headline: 'Tailored Odoo Workflows & Reports',
    description: 'Adapting Odoo to fit your exact workflows — custom reports, views, business rules, automation, and UX enhancements.',
    overview: 'Every business is unique. I customize Odoo\'s existing modules to align with your specific processes — from modified approval workflows and custom PDF reports to tailored dashboards and automated email notifications. No unnecessary complexity, just the right changes to make Odoo work exactly the way you need it.',
    benefits: ['Workflows that match your actual business processes', 'Custom reports and dashboards for better insights', 'Automated notifications and approval chains', 'Improved user experience and productivity', 'Minimal disruption to standard Odoo features', 'Upgrade-safe customizations'],
    process: ['Workflow Analysis', 'Customization Specification', 'Development & Testing', 'User Review & Feedback', 'Deployment & Documentation'],
    technologies: ['Python', 'OWL', 'QWeb Templating', 'Automated Actions', 'Scheduled Actions', 'Email Templates'],
    industries: ['All industries using Odoo ERP'],
    faqs: [
      { q: 'What\'s the difference between customization and development?', a: 'Customization modifies existing Odoo behavior (views, workflows, reports). Development creates entirely new modules or features.' },
      { q: 'How do you ensure customizations are upgrade-safe?', a: 'I use Odoo\'s inheritance mechanisms and follow official development guidelines to ensure compatibility with future versions.' },
    ],
  },
  'odoo-migration': {
    slug: 'odoo-migration',
    title: 'Odoo Migration',
    headline: 'Seamless Odoo Version Upgrades',
    description: 'Version upgrades and data migration between Odoo versions with zero data loss and minimal downtime.',
    overview: 'Staying on an outdated Odoo version means missing out on security patches, performance improvements, and new features. I handle the complete migration process — from code analysis and module compatibility checks to data migration, testing, and production cutover — ensuring a smooth transition with minimal downtime.',
    benefits: ['Access to latest Odoo features and security patches', 'Zero data loss with comprehensive validation', 'Custom module migration and compatibility updates', 'Minimal business downtime during cutover', 'Performance optimization post-migration', 'Complete regression testing'],
    process: ['Version Gap Analysis', 'Module Compatibility Audit', 'Migration Planning', 'Database Migration', 'Custom Module Updates', 'Comprehensive Testing', 'Production Cutover', 'Post-Migration Support'],
    technologies: ['Odoo Migration Scripts', 'Python', 'PostgreSQL', 'OpenUpgrade', 'Docker'],
    industries: ['All industries using Odoo ERP'],
    faqs: [
      { q: 'How long does a migration take?', a: 'Typically 2-6 weeks depending on the number of custom modules and data volume. I provide a detailed timeline after the initial audit.' },
      { q: 'Will I lose any data during migration?', a: 'No. I perform thorough data validation at every step, with rollback plans in place for safety.' },
    ],
  },
  'website-development': {
    slug: 'website-development',
    title: 'Website Development',
    headline: 'Professional Websites & eCommerce',
    description: 'Professional websites and e-commerce platforms using WordPress, WooCommerce, and custom solutions.',
    overview: 'From corporate websites and landing pages to full e-commerce platforms, I build professional web solutions that drive business results. Whether you need a WordPress site with a custom theme or a bespoke web application, I deliver fast, responsive, and SEO-optimized websites.',
    benefits: ['Mobile-responsive designs that work on all devices', 'SEO-optimized from the ground up', 'Fast loading speeds and Core Web Vitals compliance', 'E-commerce capabilities with WooCommerce', 'Content management system for easy updates', 'Ongoing maintenance and support'],
    process: ['Requirements & Wireframing', 'Design Mockup & Approval', 'Development & Content Integration', 'SEO Optimization', 'Testing & Launch', 'Training & Handover'],
    technologies: ['WordPress', 'WooCommerce', 'PHP', 'JavaScript', 'HTML/CSS', 'MySQL'],
    industries: ['All industries'],
    faqs: [
      { q: 'Do you build only WordPress sites?', a: 'While WordPress is my primary platform for websites, I also build custom web applications using modern frameworks when the project requires it.' },
      { q: 'Can you redesign my existing website?', a: 'Yes. I can redesign your existing site or migrate it to a new platform while preserving SEO rankings and content.' },
    ],
  },
  'custom-software': {
    slug: 'custom-software',
    title: 'Custom Software',
    headline: 'Bespoke Web Applications & Systems',
    description: 'Custom web applications and backend systems built with Python, PHP, and modern frameworks tailored to your specific workflow.',
    overview: 'When off-the-shelf solutions don\'t fit, I build custom web applications from scratch. From CRM systems and booking platforms to inventory management tools and customer portals, I develop scalable, secure software tailored to your exact requirements.',
    benefits: ['Built exactly to your specifications', 'Scalable architecture for future growth', 'Secure by design with industry best practices', 'RESTful APIs for integration capabilities', 'Comprehensive documentation and training', 'Full source code ownership'],
    process: ['Discovery & Requirements', 'Architecture & Technical Design', 'Agile Development Sprints', 'Testing & QA', 'Deployment & DevOps Setup', 'Training & Documentation'],
    technologies: ['Python', 'PHP', 'CodeIgniter', 'PostgreSQL', 'MySQL', 'REST APIs', 'Docker'],
    industries: ['All industries'],
    faqs: [
      { q: 'What kind of applications can you build?', a: 'CRM systems, booking platforms, property management tools, inventory systems, customer portals, and any web-based business application.' },
      { q: 'How do you ensure security?', a: 'I follow OWASP security guidelines, implement proper authentication/authorization, use prepared statements, and conduct security testing.' },
    ],
  },
  'cloud-devops': {
    slug: 'cloud-devops',
    title: 'Cloud & DevOps',
    headline: 'Cloud Infrastructure & Automation',
    description: 'Cloud infrastructure setup, server administration, Docker deployments, CI/CD pipelines, and scalable hosting solutions.',
    overview: 'I set up and manage cloud infrastructure that keeps your applications running smoothly. From initial server provisioning and security hardening to Docker containerization, CI/CD pipelines, and automated backups, I ensure your systems are fast, secure, and reliable.',
    benefits: ['Optimized server performance and uptime', 'Automated deployments with CI/CD', 'Docker containerization for consistency', 'Security hardening and SSL setup', 'Automated backups and disaster recovery', 'Cost-optimized cloud architecture'],
    process: ['Infrastructure Assessment', 'Architecture Design', 'Server Provisioning & Setup', 'Security Hardening', 'CI/CD Pipeline Setup', 'Monitoring & Alerting', 'Documentation'],
    technologies: ['AWS', 'DigitalOcean', 'Docker', 'Nginx', 'Linux', 'GitHub Actions', 'SSL/TLS'],
    industries: ['All industries'],
    faqs: [
      { q: 'Which cloud providers do you work with?', a: 'Primarily AWS and DigitalOcean, but I can work with any Linux-based cloud provider.' },
      { q: 'Can you manage our existing servers?', a: 'Yes. I offer server administration services including security updates, performance tuning, and monitoring setup.' },
    ],
  },
  'ai-solutions': {
    slug: 'ai-solutions',
    title: 'AI Solutions',
    headline: 'AI-Powered Odoo Integrations',
    description: 'AI-powered Odoo integrations — email automation, OCR invoice capture, natural language ERP queries, KPI dashboards, and more.',
    overview: 'I integrate AI capabilities directly into Odoo ERP to automate repetitive tasks and unlock new insights. From AI-powered email writing and OCR invoice capture to natural language data queries and KPI dashboard narratives, these solutions are built as production-ready Odoo modules — not experiments.',
    benefits: ['Automate repetitive data entry tasks', 'Extract data from invoices and documents with OCR', 'Query your ERP data in natural language', 'AI-generated executive summaries and reports', 'Bring your own API key — no vendor lock-in', 'Production-ready Odoo modules, not prototypes'],
    process: ['Use Case Assessment', 'AI Model Selection', 'Module Development', 'Integration Testing', 'Deployment & Training'],
    technologies: ['OpenAI API', 'Claude API', 'Ollama', 'Python', 'OCR', 'LLM', 'RAG'],
    industries: ['All industries using Odoo ERP'],
    faqs: [
      { q: 'Do I need to pay for AI API access?', a: 'Yes — you\'ll need API keys from providers like OpenAI or Anthropic. My modules use a BYO-key model so you maintain full control and there\'s no vendor lock-in.' },
      { q: 'Are these available on the Odoo App Store?', a: 'Yes — many of my AI modules are published on the official Odoo App Store and can be installed directly.' },
    ],
  },
};
