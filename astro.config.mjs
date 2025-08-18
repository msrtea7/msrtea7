// @ts-check
import { defineConfig } from 'astro/config';
import mdx from '@astrojs/mdx';


// https://astro.build/config
export default defineConfig({
    site: 'https://msrtea7.com',
    integrations: [mdx()],
    markdown: {
        shikiConfig: {
            theme: 'gruvbox-light-hard',
        },
    },
});