var itemId = null;
var similarOffset = 0;

const splits = location.pathname.split('/');
if (splits.length === 3) {
    itemId = splits[1] + ':' + splits[2];
    // mark read
    chrome.runtime.sendMessage({ read: itemId }, () => { });
    // get neighbors
    chrome.runtime.sendMessage({ neighbors: itemId, offset: similarOffset }, function (repositories) {
        renderSimilarDiv(repositories);
    });
} else if (splits.length === 2) {
    let exploreDiv = $("[aria-label='Explore']");
    exploreDiv.children("h2.f5").remove();
    exploreDiv.children("div.py-2").remove();
    exploreDiv.children("a.f6").remove();
    chrome.runtime.sendMessage({ recommend: [] }, function (result) {
        if (result.has_login) {
            showRecommend(result);
        } else {
            const login = $('meta[name=user-login]').attr('content');
            fetch(`https://api.github.com/users/${login}/starred?per_page=100`).then(r => r.json()).then(result => {
                let repoNames = result.map((value) => {
                    return value.full_name.replace('/', ':');
                })
                chrome.runtime.sendMessage({ recommend: repoNames }, function (repos) {
                    result.recommend = repos.map((value) => {
                        return value.Id;
                    });
                    showRecommend(result);
                });
            });
        }
    });
}

async function renderSimilarDiv(repositories) {
    // Create promises
    let responses = [];
    for (const repository of repositories) {
        const name = repository.Id.replace(':', '/');
        responses.push(fetchRepo(name));
    }
    Promise.all(responses).then((res) => {
        let count = 0;
        let rows = "";
        if (res.length > 0) {
            for (const [i, info] of res.entries()) {
                if (info['full_name']) {
                    let actualName = info['full_name'].replace('/', ':').toLowerCase();
                    let expectedName = repositories[i].Id.toLowerCase();
                    if (actualName != expectedName) {
                        // The repository has been renamed.
                        chrome.runtime.sendMessage({ delete: repositories[i].Id }, (r) => { console.log(r) });
                    } else if (count < 3) {
                        count++;
                        rows += `
<div class="py-2 my-2 color-border-muted">
    <a class="f6 text-bold Link--primary d-flex no-underline wb-break-all d-inline-block" href="/${info['full_name']}">${info['full_name']}</a>
    <p class="f6 color-fg-muted mb-2" itemprop="description">${info['description'] ? info['description'] : ''}</p>
    ${renderLanguageSpan(info.language)}
    <span class="f6 color-fg-muted text-normal">
        <svg aria-label="star" role="img" height="16" viewBox="0 0 16 16" version="1.1" width="16" data-view-component="true" class="octicon octicon-star">
            <path fill-rule="evenodd" d="M8 .25a.75.75 0 01.673.418l1.882 3.815 4.21.612a.75.75 0 01.416 1.279l-3.046 2.97.719 4.192a.75.75 0 01-1.088.791L8 12.347l-3.766 1.98a.75.75 0 01-1.088-.79l.72-4.194L.818 6.374a.75.75 0 01.416-1.28l4.21-.611L7.327.668A.75.75 0 018 .25zm0 2.445L6.615 5.5a.75.75 0 01-.564.41l-3.097.45 2.24 2.184a.75.75 0 01.216.664l-.528 3.084 2.769-1.456a.75.75 0 01.698 0l2.77 1.456-.53-3.084a.75.75 0 01.216-.664l2.24-2.183-3.096-.45a.75.75 0 01-.564-.41L8 2.694v.001z"></path>
        </svg>
        ${info['stargazers_count']}
    </span>
</div>`
                    }
                } else if (info.message == 'Not Found') {
                    // The repository has been removed.
                    chrome.runtime.sendMessage({ delete: repositories[i].Id }, () => { });
                }
            }
        } else {
            rows = '<div class="text-small color-fg-muted">No similar repositories found</div>'
        }
        // Render previous button
        let previous = similarOffset > 0 ?
            `<a id="previous-button" class="text-small" href="#">🡠 Previous</a>` :
            '<span id="previous-button" class="text-small color-fg-muted">🡠 Previous</span>';
        // Render next button
        let next = similarOffset < 9 ?
            `<a id="next-button" class="text-small" style="float: right" href="#">Next 🡢</a>` :
            `<span id="next-button" class="text-small color-fg-muted" style="float: right">Next 🡢</span>`;
        template = `
<div class="BorderGrid-row" id="similar-repositories">
    <div class="BorderGrid-cell">
        <h2 class="h4 mb-3">Related repositories</h2>
        ${rows}${previous}${next}
    </div>
</div>`;
        $("#similar-repositories").remove();
        $(".BorderGrid:first").append($($.parseHTML(template)));
        $("a#previous-button").click(function () {
            $("#previous-button").remove();
            $("#next-button").remove();
            similarOffset -= 3;
            chrome.runtime.sendMessage({ neighbors: itemId, offset: similarOffset }, function (repositories) {
                renderSimilarDiv(repositories);
            });
            return false;
        });
        $("a#next-button").click(function () {
            $("#previous-button").remove();
            $("#next-button").remove();
            similarOffset += 3;
            chrome.runtime.sendMessage({ neighbors: itemId, offset: similarOffset }, function (repositories) {
                renderSimilarDiv(repositories);
            });
            return false;
        });
    })
}

async function showRecommend(result) {
    let responses = [];
    for (const repository of result.recommend) {
        const name = repository.replace(':', '/');
        responses.push(fetchRepo(name));
    }
    Promise.all(responses).then((res) => {
        let exploreDiv = $("[aria-label='Explore']");
        exploreDiv.children("h2.f5").remove();
        exploreDiv.children("div.py-2").remove();
        exploreDiv.children("a.f6").remove();
        let template = `<h2 class="f5 text-bold mb-1">Explore repositories <a href="https://gitrec.gorse.io" target="_blank">by GitRec</a></h2>`;
        exploreDiv.append($($.parseHTML(template)));
        if (res.length > 0) {
            for (const [i, info] of res.entries()) {
                if (info['full_name']) {
                    let row = `
<div class="py-2 my-2${i == res.length - 1 ? '' : ' border-bottom color-border-muted'}">
    <a class="f6 text-bold Link--primary d-flex no-underline wb-break-all d-inline-block" href="/${info['full_name']}">${info['full_name']}</a>
    <p class="f6 color-fg-muted mb-2" itemprop="description">${info['description'] ? info['description'] : ''}</p>
    ${renderLanguageSpan(info.language)}
    <span class="f6 color-fg-muted text-normal">
        <svg aria-label="star" role="img" height="16" viewBox="0 0 16 16" version="1.1" width="16" data-view-component="true" class="octicon octicon-star">
            <path fill-rule="evenodd" d="M8 .25a.75.75 0 01.673.418l1.882 3.815 4.21.612a.75.75 0 01.416 1.279l-3.046 2.97.719 4.192a.75.75 0 01-1.088.791L8 12.347l-3.766 1.98a.75.75 0 01-1.088-.79l.72-4.194L.818 6.374a.75.75 0 01.416-1.28l4.21-.611L7.327.668A.75.75 0 018 .25zm0 2.445L6.615 5.5a.75.75 0 01-.564.41l-3.097.45 2.24 2.184a.75.75 0 01.216.664l-.528 3.084 2.769-1.456a.75.75 0 01.698 0l2.77 1.456-.53-3.084a.75.75 0 01.216-.664l2.24-2.183-3.096-.45a.75.75 0 01-.564-.41L8 2.694v.001z"></path>
        </svg>
    ${info['stargazers_count']}
    </span>
</div>`
                    exploreDiv.append($($.parseHTML(row)));
                } else if (info.message == 'Not Found') {
                    chrome.runtime.sendMessage({ delete: result.recommend[i] }, () => { });
                }
            }
        }
        if (result.has_login) {
            template = `
<a class="d-block Link--secondary no-underline f6 mb-3" href="#" id="renew-button">
    Renew recommendation →
</a>`
        } else {
            template = `
<a class="d-block Link--secondary no-underline f6 mb-3" href="https://gitrec.gorse.io" target="_blank">
    Login GitRec for better recommendation →
</a>`
        }
        exploreDiv.append($($.parseHTML(template)));
        $("a#renew-button").click(function () {
            $("#renew-button").remove();
            chrome.runtime.sendMessage({ read: result.recommend }, () => {
                chrome.runtime.sendMessage({ recommend: [] }, function (result) {
                    showRecommend(result);
                });
            });
            return false;
        });
    })
}

async function fetchRepo(name) {
    let response = await fetch(`https://api.github.com/repos/${name}`);
    return await response.json();
}

function renderLanguageSpan(language) {
    if (language) {
        return `
<span class="mr-2 f6 color-fg-muted text-normal">
    <span class="">
        <span class="repo-language-color" style="background-color: ${renderLanguageColor(language)}"></span>
        <span itemprop="programmingLanguage">${language}</span>
    </span>
</span>`;
    } else {
        return '';
    }
}
