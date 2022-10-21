import { GM_xmlhttpRequest } from 'vite-plugin-monkey/dist/client';

const api = {
    read: async ({ itemId }: { itemId: string }) => {
        return new Promise((res, rej) => {
            GM_xmlhttpRequest({
                url: `https://gitrec.gorse.io/api/read/${itemId}`,
                method: 'POST',
                onload(response) {
                    res(JSON.parse(response.responseText));
                },
                onerror(response) {
                    rej(response);
                },
            });
        });
    },
    delete: async ({ itemId }: { itemId: string }) => {
        return new Promise((res, rej) => {
            GM_xmlhttpRequest({
                url: `https://gitrec.gorse.io/api/delete/${itemId}`,
                method: 'POST',
                onload(response) {
                    res(JSON.parse(response.responseText));
                },
                onerror(response) {
                    rej(response);
                },
            });
        });
    },
    neighbors: async ({
        neighbors,
        offset,
    }: {
        neighbors: string;
        offset: string | number;
    }) => {
        return new Promise((res, rej) => {
            GM_xmlhttpRequest({
                url: `https://gitrec.gorse.io/api/v2/neighbors/${neighbors}?offset=${offset}&n=6`,
                onload(response) {
                    res(JSON.parse(response.responseText));
                },
                onerror(response) {
                    rej(response);
                },
            });
        });
    },
    recommendSession: async ({ recommend }: { recommend: unknown[] }) => {
        return new Promise((res, rej) => {
            GM_xmlhttpRequest({
                url: `https://gitrec.gorse.io/api/v2/session/recommend?n=6`,
                method: 'POST',
                data: JSON.stringify(recommend),
                onload(response) {
                    res(JSON.parse(response.responseText));
                },
                onerror(response) {
                    rej(response);
                },
            });
        });
    },
    recommendExtension: async () => {
        return new Promise((res, rej) => {
            GM_xmlhttpRequest({
                url: `https://gitrec.gorse.io/api/v2/extension/recommend`,
                onload(response) {
                    res(JSON.parse(response.responseText));
                },
                onerror(response) {
                    rej(response);
                },
            });
        });
    },
} as const;

export default api;
