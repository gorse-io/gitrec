var titleTemplate = `
<h2 class="f5 text-bold mb-1" style="display:inline-block">Explore repositories</h2>
<details class="details-reset details-overlay dropdown float-right mt-1">
    <summary class="pinned-items-setting-link Link--muted" aria-haspopup="menu" role="button">
        Explore settings
        <div class="dropdown-caret"></div>
    </summary>

    <details-menu class="dropdown-menu dropdown-menu-sw contributions-setting-menu" role="menu" style="width: 240px">
        <button id="gitrec-button" class="dropdown-item ws-normal btn-link text-left pl-5" role="menuitem">
            <div class="text-bold">Explore GitRec</div>
            <span class="f6 mt-1">
            Explore repositories from GitRec based on starred repositories.
            </span>
        </button>
        <div role="none" class="dropdown-divider"></div>
        <button id="github-button" value="1" class="dropdown-item ws-normal btn-link text-left pl-5" role="menuitem">
            <div class="d-flex flex-items-center text-bold">Explore GitHub</div>
            <span class="f6 mt-1">
            Explore repositories from GitHub official recommendation.
            </span>
        </button>
    </details-menu>
</details>`;

var itemId = null;
var similarOffset = 0;
var exploreContent = null;

$(document).ready(function () {
    const splits = location.pathname.split('/').filter(s => s);
    if (splits.length === 2) {
        itemId = splits[0] + ':' + splits[1];
        // mark read
        chrome.runtime.sendMessage({ read: itemId }, () => { });
        // get neighbors
        loadSimilarRepos();
    } else if (splits.length === 0) {
        // reset title
        let exploreDiv = $("[aria-label='Explore repositories']");
        if (exploreContent == null) {
            exploreContent = exploreDiv.children("div[data-view-component=true]");
        }
        exploreDiv.children("h2.f5").remove();
        exploreDiv.children("details").remove();
        exploreDiv.children("div.py-2").remove();
        exploreDiv.children("a.f6").remove();
        exploreDiv.append($($.parseHTML(titleTemplate)));
        $("#gitrec-button").click(function () {
            chrome.storage.sync.set({ explore: 'gitrec' }, function () {
                selectExploreSettings('gitrec');
                loadRecommendRepos();
            });
            return false;
        });
        $("#github-button").click(function () {
            chrome.storage.sync.set({ explore: 'github' }, function () {
                selectExploreSettings('github');
                loadRecommendRepos();
            });
            return false;
        });
        chrome.storage.sync.get(['explore'], function (result) {
            if (result.explore == 'github') {
                selectExploreSettings('github');
            } else {
                selectExploreSettings('gitrec');
            }
        });
        // get recommend
        loadRecommendRepos();
    }
})

function loadSimilarRepos() {
    chrome.runtime.sendMessage({ neighbors: itemId, offset: similarOffset }, function (result) {
        if (result.is_authenticated) {
            renderSimilarDiv(result);
        } else {
            // Fetch repos in client-side
            let responses = [];
            for (const score of result.scores) {
                const full_name = score.Id.replace(':', '/');
                responses.push(fetchRepo(full_name));
            }
            Promise.all(responses).then((repos) => {
                result.repos = repos;
                for (const [i, score] of result.scores.entries()) {
                    if (repos[i].full_name) {
                        result.repos[i].item_id = score.Id;
                    } else {
                        result.message = repos[i].message;
                    }
                }
                renderSimilarDiv(result);
            })
        }
    });
}

async function renderSimilarDiv(result) {
    let count = 0;
    let rows = "";
    let previous = "";
    let next = "";
    if (result.message) {
        let errorMessage = "";
        if (result.message.startsWith('API rate limit exceeded')) {
            errorMessage = `API rate limit exceeded. Login <a href="https://gitrec.gorse.io" target="_blank">GitRec</a> to get a higher rate limit.`
        } else {
            errorMessage = result.message;
        }
        rows = `<div class="text-small color-fg-muted">${errorMessage}</div>`
    } else if (result.repos.length > 0) {
        for (const repo of result.repos) {
            if (repo.full_name) {
                if (repo.item_id != repo.full_name.replace('/', ':').toLowerCase()) {
                    // The repository has been renamed.
                    chrome.runtime.sendMessage({ delete: repo.item_id }, () => { });
                } else if (count < 3) {
                    count++;
                    rows += `
<div class="py-2 my-2 color-border-muted">
    <a class="f6 text-bold Link--primary d-flex no-underline wb-break-all d-inline-block" href="/${repo.full_name}">${repo.full_name}</a>
    <p class="f6 color-fg-muted mb-2" itemprop="description">${repo.description ? repo.description : ''}</p>
    ${renderLanguageSpan(repo.language)}
    <span class="f6 color-fg-muted text-normal">
        <svg aria-label="star" role="img" height="16" viewBox="0 0 16 16" version="1.1" width="16" data-view-component="true" class="octicon octicon-star">
            <path fill-rule="evenodd" d="M8 .25a.75.75 0 01.673.418l1.882 3.815 4.21.612a.75.75 0 01.416 1.279l-3.046 2.97.719 4.192a.75.75 0 01-1.088.791L8 12.347l-3.766 1.98a.75.75 0 01-1.088-.79l.72-4.194L.818 6.374a.75.75 0 01.416-1.28l4.21-.611L7.327.668A.75.75 0 018 .25zm0 2.445L6.615 5.5a.75.75 0 01-.564.41l-3.097.45 2.24 2.184a.75.75 0 01.216.664l-.528 3.084 2.769-1.456a.75.75 0 01.698 0l2.77 1.456-.53-3.084a.75.75 0 01.216-.664l2.24-2.183-3.096-.45a.75.75 0 01-.564-.41L8 2.694v.001z"></path>
        </svg>
        ${repo.stargazers_count}
    </span>
</div>`
                }
            } else if (repo.message == 'Not Found') {
                // The repository has been removed.
                chrome.runtime.sendMessage({ delete: repo.item_id }, () => { });
            }
        }
        // Render previous button
        previous = similarOffset > 0 ?
            `<a id="previous-button" class="text-small" href="#">← Previous</a>` :
            '<span id="previous-button" class="text-small color-fg-muted">← Previous</span>';
        // Render next button
        next = similarOffset < 9 ?
            `<a id="next-button" class="text-small" style="float: right" href="#">Next →</a>` :
            `<span id="next-button" class="text-small color-fg-muted" style="float: right">Next →</span>`;
    } else {
        rows = '<div class="text-small color-fg-muted">No similar repositories found</div>'
    }
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
        loadSimilarRepos();
        return false;
    });
    $("a#next-button").click(function () {
        $("#previous-button").remove();
        $("#next-button").remove();
        similarOffset += 3;
        loadSimilarRepos();
        return false;
    });
}

function loadRecommendRepos() {
    let exploreDiv = $("[aria-label='Explore repositories']");
    exploreDiv.children("div[data-view-component=true]").remove();
    exploreDiv.children("div.py-2").remove();
    exploreDiv.children("a.f6").remove();
    exploreDiv.children("#error-message").remove();
    chrome.storage.sync.get(['explore'], function (result) {
        if (result.explore != 'github') {
            chrome.runtime.sendMessage({ recommend: [] }, function (result) {
                if (result.is_authenticated) {
                    showRecommend(result);
                } else {
                    const login = $('meta[name=user-login]').attr('content');
                    fetch(`https://api.github.com/users/${login}/starred?per_page=100`).then(r => r.json()).then(result => {
                        if (result.message) {
                            showRecommend(result);
                        } else {
                            let repoNames = result.map((value) => {
                                return value.full_name.replace('/', ':');
                            })
                            chrome.runtime.sendMessage({ recommend: repoNames }, function (scores) {
                                // Fetch repos in client-side
                                let responses = [];
                                for (const score of scores) {
                                    const full_name = score.Id.replace(':', '/');
                                    responses.push(fetchRepo(full_name));
                                }
                                Promise.all(responses).then((repos) => {
                                    result.repos = repos;
                                    for (const [i, score] of scores.entries()) {
                                        result.repos[i].item_id = score.Id;
                                    }
                                    showRecommend(result);
                                })
                            });
                        }
                    });
                }
            });
        } else {
            exploreDiv.append(exploreContent);
        }
    });
}

async function showRecommend(result) {
    let exploreDiv = $("[aria-label='Explore repositories']");
    exploreDiv.children("div.py-2").remove();
    exploreDiv.children("a.f6").remove();
    exploreDiv.children("#error-message").remove();
    if (result.message) {
        let errorMessage = "";
        if (result.message.startsWith('API rate limit exceeded')) {
            errorMessage = `API rate limit exceeded. Login <a href="https://gitrec.gorse.io" target="_blank">GitRec</a> to get a higher rate limit.`
        } else {
            errorMessage = result.message;
        }
        template = `<div class="d-block no-underline f6 mb-3" id="error-message">${errorMessage}</div>`
    } else if (result.repos.length > 0) {
        for (const [i, repo] of result.repos.entries()) {
            let row = `
<div class="py-2 my-2${i == result.repos.length - 1 ? '' : ' border-bottom color-border-muted'}">
    <a class="f6 text-bold Link--primary d-flex no-underline wb-break-all d-inline-block" href="/${repo.full_name}">${repo.full_name}</a>
    <p class="f6 color-fg-muted mb-2" itemprop="description">${repo.description ? repo.description : ''}</p>
    ${renderLanguageSpan(repo.language)}
    <span class="f6 color-fg-muted text-normal">
        <svg aria-label="star" role="img" height="16" viewBox="0 0 16 16" version="1.1" width="16" data-view-component="true" class="octicon octicon-star">
            <path fill-rule="evenodd" d="M8 .25a.75.75 0 01.673.418l1.882 3.815 4.21.612a.75.75 0 01.416 1.279l-3.046 2.97.719 4.192a.75.75 0 01-1.088.791L8 12.347l-3.766 1.98a.75.75 0 01-1.088-.79l.72-4.194L.818 6.374a.75.75 0 01.416-1.28l4.21-.611L7.327.668A.75.75 0 018 .25zm0 2.445L6.615 5.5a.75.75 0 01-.564.41l-3.097.45 2.24 2.184a.75.75 0 01.216.664l-.528 3.084 2.769-1.456a.75.75 0 01.698 0l2.77 1.456-.53-3.084a.75.75 0 01.216-.664l2.24-2.183-3.096-.45a.75.75 0 01-.564-.41L8 2.694v.001z"></path>
        </svg>
    ${repo.stargazers_count}
    </span>
</div>`
            exploreDiv.append($($.parseHTML(row)));
        }
        if (result.is_authenticated) {
            template = `
    <a class="d-block Link--secondary no-underline f6 mb-3" href="#" id="renew-button">
        Next batch →
    </a>`
        } else {
            template = `
    <a class="d-block Link--secondary no-underline f6 mb-3" href="https://gitrec.gorse.io" target="_blank">
        Login GitRec for better recommendation →
    </a>`
        }
    }
    exploreDiv.append($($.parseHTML(template)));
    $("a#renew-button").click(function () {
        $("#renew-button").remove();
        chrome.runtime.sendMessage({ read: result.items }, () => {
            chrome.runtime.sendMessage({ recommend: [] }, function (result) {
                showRecommend(result);
            });
        });
        return false;
    });
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

function selectExploreSettings(setting) {
    $("#explore-settings-select-menu-item-icon").remove();
    const template = `
<svg id="explore-settings-select-menu-item-icon" aria-hidden="true" height="16" viewBox="0 0 16 16" version="1.1" width="16" data-view-component="true" class="octicon octicon-check select-menu-item-icon mt-1">
    <path fill-rule="evenodd" d="M13.78 4.22a.75.75 0 010 1.06l-7.25 7.25a.75.75 0 01-1.06 0L2.22 9.28a.75.75 0 011.06-1.06L6 10.94l6.72-6.72a.75.75 0 011.06 0z"></path>
</svg>`;
    let button = $(`#${setting}-button`);
    button.prepend($($.parseHTML(template)));
}
