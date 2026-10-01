const assert = require('node:assert/strict');
const { readFileSync } = require('node:fs');
const { join } = require('node:path');
const { test } = require('node:test');
const { JSDOM } = require('jsdom');

const source = name => readFileSync(join(__dirname, '..', name), 'utf8');
const tick = () => new Promise(resolve => setTimeout(resolve, 180));
const sidebar = '<div class="CodeViewSidebar-module__borderGrid__newHash"></div>';
const repos = name => ({ is_authenticated: true, repos: [{
    full_name: name, item_id: name.replace('/', ':').toLowerCase(),
    description: 'A related repository', language: 'Go', stargazers_count: 42,
}] });

function page(t, markup = sidebar) {
    const dom = new JSDOM(`<meta name="octolytics-dimension-repository_nwo" content="owner/first">${markup}`, {
        url: 'https://github.com/owner/first', runScripts: 'outside-only',
    });
    t.after(() => dom.window.close());
    const requests = [];
    const listeners = [];
    dom.window.chrome = { runtime: {
        sendMessage(message, callback) { requests.push({ message, callback }); },
        onMessage: { addListener(callback) { listeners.push(callback); } },
    } };
    for (const file of ['jquery-3.6.1.min.js', 'colors.js', 'content.js']) dom.window.eval(source(file));
    return { window: dom.window, document: dom.window.document, requests, listeners };
}

test('new sidebar works without a Star counter and pagination renders only once', async t => {
    const p = page(t);
    await tick();
    const first = p.requests.find(r => r.message.neighbors);
    assert.equal(first.message.neighbors, 'owner:first');
    first.callback(repos('related/one'));
    assert.equal(p.document.querySelector('#similar-repositories a').textContent, 'related/one');
    p.document.querySelector('#next-button').click();
    const next = p.requests.filter(r => r.message.neighbors).at(-1);
    assert.equal(next.message.offset, 3);
    next.callback(repos('related/two'));
    assert.ok(p.document.querySelector('#previous-button'));
    p.document.querySelector('#previous-button').click();
    assert.equal(p.requests.filter(r => r.message.neighbors).at(-1).message.offset, 0);
    p.window.eval(source('content.js'));
    await tick();
    assert.equal(p.listeners.length, 1);
    assert.equal(p.document.querySelectorAll('#similar-repositories').length, 1);
});

test('waits for a delayed sidebar and restores the panel after React replaces it', async t => {
    const p = page(t, '');
    await tick();
    assert.equal(p.requests.length, 0);
    p.document.body.innerHTML = sidebar;
    await tick();
    const request = p.requests.find(r => r.message.neighbors);
    // The view disappears while the network response is in flight.
    p.document.body.innerHTML = '';
    request.callback(repos('related/one'));
    p.document.body.innerHTML = sidebar;
    await tick();
    assert.ok(p.document.querySelector('#similar-repositories'));
    p.document.body.innerHTML = sidebar;
    await tick();
    assert.ok(p.document.querySelector('#similar-repositories'));
    assert.equal(p.requests.filter(r => r.message.neighbors).length, 1);
});

test('navigation resets pagination, waits for matching metadata, and ignores stale responses', async t => {
    const p = page(t);
    await tick();
    const old = p.requests.find(r => r.message.neighbors);
    p.window.history.pushState({}, '', '/owner/second');
    p.listeners[0]({ navigation: true });
    await tick();
    old.callback(repos('wrong/repository'));
    assert.equal(p.document.querySelector('#similar-repositories'), null);
    assert.equal(p.requests.filter(r => r.message.neighbors).length, 1);
    p.document.querySelector('meta').content = 'owner/second';
    p.document.body.innerHTML = sidebar;
    await tick();
    const current = p.requests.filter(r => r.message.neighbors).at(-1);
    assert.equal(current.message.neighbors, 'owner:second');
    assert.equal(current.message.offset, 0);
    current.callback(repos('correct/repository'));
    assert.match(p.document.querySelector('#similar-repositories').textContent, /correct\/repository/);
    p.window.history.pushState({}, '', '/owner/second/issues');
    p.document.body.innerHTML = '<main>Issues</main>';
    p.listeners[0]({ navigation: true });
    await tick();
    assert.equal(p.document.querySelector('#similar-repositories'), null);
    p.window.history.back();
    p.document.body.innerHTML = sidebar;
    await tick();
    assert.equal(p.requests.filter(r => r.message.neighbors).length, 3);
});

test('legacy sidebar still works and failed responses show an error', async t => {
    const p = page(t, '<div class="Layout-sidebar"><div class="BorderGrid"></div></div>');
    await tick();
    p.requests.find(r => r.message.neighbors).callback(undefined);
    assert.match(p.document.querySelector('#similar-repositories').textContent, /Unable to load/);
});

test('anonymous results fetch repository details and network failures stay visible', async t => {
    const p = page(t);
    p.window.fetch = async () => ({ json: async () => repos('related/one').repos[0] });
    await tick();
    p.requests.find(r => r.message.neighbors).callback({ is_authenticated: false, scores: [{ Id: 'related:one' }] });
    await tick();
    assert.match(p.document.querySelector('#similar-repositories').textContent, /related\/one/);
    p.window.fetch = async () => { throw new Error('offline'); };
    p.document.querySelector('#next-button').click();
    p.requests.filter(r => r.message.neighbors).at(-1).callback({ is_authenticated: false, scores: [{ Id: 'related:two' }] });
    await tick();
    assert.match(p.document.querySelector('#similar-repositories').textContent, /Unable to load/);
});
