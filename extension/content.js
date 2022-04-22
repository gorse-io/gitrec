// Get repo name
const splits = location.pathname.split('/');
if (splits.length === 3) {
    fetch('https://gitrec.gorse.io/api/neighbors/' + splits[1] + ':' + splits[2]).then(r => r.json()).then(result => {
        showSimilar(result);
    })
} else if (splits.length === 2) {
    const login = document.querySelector('meta[name=\'user-login\']').content;
    fetch('https://api.github.com/users/' + login + '/starred?per_page=100').then(r => r.json()).then(result => {
        let repoNames = result.map((value) => {
            return value.full_name.replace('/', ':');
        })
        showRecommend(login, repoNames)
    })
}

async function showSimilar(repositories) {
    // Create promises
    let responses = [];
    for (const repository of repositories) {
        const name = repository.Id.replace(':', '/');
        responses.push(getRepo(name));
    }
    Promise.all(responses).then((res) => {
        let template = "";
        if (res.length > 0) {
            for (const info of res) {
                template += `<div class="py-2 my-2 color-border-muted">
        <a class="f6 text-bold Link--primary d-flex no-underline wb-break-all d-inline-block" href="/` + info['full_name'] + `">` + info['full_name'] + `</a>` + getDescription(info) + getLanguage(info) + `
          <span class="f6 color-fg-muted text-normal">
            <svg aria-label="star" role="img" height="16" viewBox="0 0 16 16" version="1.1" width="16" data-view-component="true" class="octicon octicon-star">
              <path fill-rule="evenodd" d="M8 .25a.75.75 0 01.673.418l1.882 3.815 4.21.612a.75.75 0 01.416 1.279l-3.046 2.97.719 4.192a.75.75 0 01-1.088.791L8 12.347l-3.766 1.98a.75.75 0 01-1.088-.79l.72-4.194L.818 6.374a.75.75 0 01.416-1.28l4.21-.611L7.327.668A.75.75 0 018 .25zm0 2.445L6.615 5.5a.75.75 0 01-.564.41l-3.097.45 2.24 2.184a.75.75 0 01.216.664l-.528 3.084 2.769-1.456a.75.75 0 01.698 0l2.77 1.456-.53-3.084a.75.75 0 01.216-.664l2.24-2.183-3.096-.45a.75.75 0 01-.564-.41L8 2.694v.001z"></path>
            </svg>
            ` + info['stargazers_count'] + `
          </span>
        </div>`
            }
        } else {
            template = '<div class="text-small color-fg-muted">No similar repositories found</div>'
        }
        template = `<div class="BorderGrid-row"><div class="BorderGrid-cell"><h2 class="h4 mb-3">Similar repositories</h2>` + template + `</div></div>`;
        const fragment = document.createRange().createContextualFragment(template);
        const borderGrid = document.querySelector('.BorderGrid');
        borderGrid.appendChild(fragment.firstChild);
    })
}

async function showRecommend(login, repoNames) {
    fetch('https://gitrec.gorse.io/api/extension/recommend/' + login, {
        method: 'POST',
        body: JSON.stringify(repoNames),
    }).then(r => r.json()).then(result => {
        let responses = [];
        for (const repository of result.recommend) {
            const name = repository.replace(':', '/');
            responses.push(getRepo(name));
        }
        Promise.all(responses).then((res) => {
            let template = `<h2 class="f5 text-bold mb-1">Recommended repositories</h2>`;
            let fragment = document.createRange().createContextualFragment(template);
            const teamLeftColumn = document.querySelector('.team-left-column.col-md-3.col-lg-4.mt-5.hide-lg.hide-md.hide-sm.border-bottom');
            teamLeftColumn.appendChild(fragment.firstChild);
            if (res.length > 0) {
                for (const info of res) {
                    template = `<div class="py-2 my-2 border-bottom color-border-muted">
              <a class="f6 text-bold Link--primary d-flex no-underline wb-break-all d-inline-block" href="/` + info['full_name'] + `">` + info['full_name'] + `</a>` + getDescription(info) + getLanguage(info) + `<span class="f6 color-fg-muted text-normal">
              <svg aria-label="star" role="img" height="16" viewBox="0 0 16 16" version="1.1" width="16" data-view-component="true" class="octicon octicon-star">
                  <path fill-rule="evenodd" d="M8 .25a.75.75 0 01.673.418l1.882 3.815 4.21.612a.75.75 0 01.416 1.279l-3.046 2.97.719 4.192a.75.75 0 01-1.088.791L8 12.347l-3.766 1.98a.75.75 0 01-1.088-.79l.72-4.194L.818 6.374a.75.75 0 01.416-1.28l4.21-.611L7.327.668A.75.75 0 018 .25zm0 2.445L6.615 5.5a.75.75 0 01-.564.41l-3.097.45 2.24 2.184a.75.75 0 01.216.664l-.528 3.084 2.769-1.456a.75.75 0 01.698 0l2.77 1.456-.53-3.084a.75.75 0 01.216-.664l2.24-2.183-3.096-.45a.75.75 0 01-.564-.41L8 2.694v.001z"></path>
              </svg>
                  ` + info['stargazers_count'] + `
              </span>
            </div>`
                    fragment = document.createRange().createContextualFragment(template);
                    teamLeftColumn.appendChild(fragment.firstChild);
                }
            }
            if (result.has_login) {
                template = `<a class="d-block Link--secondary no-underline f6 mb-3"  href="https://gitrec.gorse.io" target="_blank">
                  Powered by GitRec →
                </a>`
            } else {
                template = `<a class="d-block Link--secondary no-underline f6 mb-3"  href="https://gitrec.gorse.io" target="_blank">
                  Login GitRec for better recommendation →
                </a>`
            }
            fragment = document.createRange().createContextualFragment(template);
            teamLeftColumn.appendChild(fragment.firstChild);
        })
    })
}

async function getRepo(name) {
    const url = "https://api.github.com/repos/" + name
    let response = await fetch(url);
    return await response.json();
}

function getLanguage(info) {
    if (info['language'] == null) {
        return '';
    }
    return `<span class="mr-2 f6 color-fg-muted text-normal">
                <span class="">
                  <span class="repo-language-color" style="background-color: ` + getColor(info['language']) + `"></span>
                    <span itemprop="programmingLanguage">` + info['language'] + `</span>
                </span>
              </span>`;
}

function getDescription(info) {
    if (info['description'] == null) {
        return '<p class="f6 color-fg-muted mb-2" itemprop="description"></p>';
    }
    return `<p class="f6 color-fg-muted mb-2" itemprop="description">` + info['description'] + `</p>`
}
