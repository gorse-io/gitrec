import { defineConfig } from 'vite';
import monkey, { cdn } from 'vite-plugin-monkey';

export default defineConfig({
    plugins: [
        monkey({
            entry: 'src/main.ts',
            userscript: {
                namespace: `gorse-io`,
                name: `GitRec`,
                description: `A recommender system for GitHub repositories based on Gorse`,
                icon: `https://gitrec.gorse.io/logo.png`,
                match: [`*://github.com/*`],
                connect: [`gitrec.gorse.io`], // GM_xmlhttpRequest 能访问的 host
            },
            build: {
                externalGlobals: {
                    jquery: cdn.jsdelivr(`$`, `dist/jquery.min.js`),
                },
            },
        }),
    ],
});
