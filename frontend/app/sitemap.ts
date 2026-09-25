import type { MetadataRoute } from 'next';

// Haqiqiy domen aniqlangach NEXT_PUBLIC_SITE_URL ni .env da sozlang;
// hozircha localhost fallback bilan ishlaydi.
const site = process.env.NEXT_PUBLIC_SITE_URL || 'http://localhost:3000';

export default function sitemap(): MetadataRoute.Sitemap {
  return [
    { url: `${site}/`, changeFrequency: 'weekly', priority: 1 },
    { url: `${site}/register`, changeFrequency: 'monthly', priority: 0.8 },
    { url: `${site}/login`, changeFrequency: 'monthly', priority: 0.5 },
  ];
}
