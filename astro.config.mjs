// @ts-check
import { defineConfig } from 'astro/config';
import mdx from '@astrojs/mdx';


import icon from 'astro-icon';


// https://astro.build/config
export default defineConfig({
    site: 'https://msrtea7.com',
    integrations: [mdx(), icon()],
    markdown: {
        shikiConfig: {
            theme: 'gruvbox-light-hard',
        },
    },
});