const assert = require('node:assert/strict');
const { readFileSync } = require('node:fs');
const { join } = require('node:path');
const { test } = require('node:test');
const { runInNewContext } = require('node:vm');

function background(fetch) {
    const listeners = {};
    const sent = [];
    runInNewContext(readFileSync(join(__dirname, '..', 'background.js'), 'utf8'), {
        fetch,
        chrome: {
            runtime: { onMessage: { addListener: fn => { listeners.message = fn; } } },
            webNavigation: { onHistoryStateUpdated: { addListener(fn, filter) {
                listeners.navigate = fn;
                listeners.filter = filter;
            } } },
            tabs: { sendMessage(tabId, message, callback) { sent.push({ tabId, message }); callback(); } },
            action: { onClicked: { addListener() {} } },
        },
    });
    return { listeners, sent };
}

test('navigation notifies each GitHub tab independently and ignores subframes', () => {
    const { listeners, sent } = background();
    assert.equal(listeners.filter.url[0].hostEquals, 'github.com');
    listeners.navigate({ tabId: 1, frameId: 0 });
    listeners.navigate({ tabId: 2, frameId: 0 });
    listeners.navigate({ tabId: 1, frameId: 3 });
    assert.deepEqual(sent.map(r => r.tabId), [1, 2]);
    assert.ok(sent.every(r => r.message.navigation));
});

test('failed neighbor fetch returns an error instead of leaving the response pending', async () => {
    const { listeners } = background(async () => { throw new Error('offline'); });
    const response = await new Promise(resolve => {
        assert.equal(listeners.message({ neighbors: 'owner:repo', offset: 0 }, {}, resolve), true);
    });
    assert.match(response.message, /Unable to load related repositories/);
});
