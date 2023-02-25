import { defineConfig } from 'vite';
import monkey, { cdn } from 'vite-plugin-monkey';

export default defineConfig({
    plugins: [
        monkey({
            entry: 'src/main.ts',
            userscript: {
                namespace: `gorse-io`,
                name: `GitRec`,
                version: `0.6`,
                description: `A recommender system for GitHub repositories based on Gorse`,
                icon: `https://gitrec.gorse.io/logo.png`,
                match: [`*://github.com/*`],
                connect: [`gitrec.gorse.io`],
                license: `WTFPL`
            },
            build: {
                externalGlobals: {
                    jquery: cdn.jsdelivr(`$`, `dist/jquery.min.js`),
                },
            },
        }),
    ],
});
