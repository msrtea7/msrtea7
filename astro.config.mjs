// @ts-check
import { defineConfig } from 'astro/config';
import mdx from '@astrojs/mdx';
import partytown from '@astrojs/partytown'


import icon from 'astro-icon';


// https://astro.build/config
export default defineConfig({
    site: 'https://msrtea7.com',
    integrations: [
        mdx(), 
        icon(), 
        partytown({
            config: {
              forward: ["dataLayer.push"],
            },
        }),
    ],
    markdown: {
        shikiConfig: {
            themes: {
                light: 'gruvbox-light-hard',
                dark: 'laserwave'
            },
            //red
            //material-theme
            //monokai
            //gruvbox-dark-hard
        },
    },
});