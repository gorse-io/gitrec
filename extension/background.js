chrome.runtime.onMessage.addListener(
    function (request, _sender, sendResponse) {
        if (request.read) {
            if (request.read instanceof Array) {
                let responses = [];
                for (const itemId of request.read) {
                    responses.push(async function () {
                        let response = await fetch(`https://gitrec.gorse.io/api/read/${itemId}`, {
                            method: 'POST',
                            credentials: 'include'
                        });
                        return await response.json();
                    }());
                }
                Promise.all(responses).then((r) => {
                    sendResponse(r);
                });
            } else {
                fetch(`https://gitrec.gorse.io/api/read/${request.read}`, {
                    method: 'POST',
                    credentials: 'include'
                }).then(r => r.json()).then(r => {
                    sendResponse(r);
                })
            }
        } else if (request.delete) {
            fetch(`https://gitrec.gorse.io/api/delete/${request.delete}`, {
                method: 'POST',
                credentials: 'include'
            }).then(r => r.json()).then(r => {
                sendResponse(r);
            })
        } else if (request.neighbors) {
            fetch(`https://gitrec.gorse.io/api/neighbors/${request.neighbors}?offset=${request.offset}`, {
                credentials: 'include'
            }).then(r => r.json()).then(r => {
                sendResponse(r);
            })
        } else if (request.recommend) {
            fetch('https://gitrec.gorse.io/api/extension/recommend', {
                credentials: 'include'
            }).then(r => r.json()).then(r => {
                sendResponse(r);
            })
        }
        return true;
    }
);
