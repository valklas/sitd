const breadcrumb = document.getElementById("breadcrumb");
const files = document.getElementById("files");

const fileIconPath = "/static/assets/icons/white/file-white-24.svg";

const directoryIconPath = "/static/assets/icons/white/file-directory-fill-white-24.svg";

const iconCache = new Map();

function getCurrentPath() {
    let path = window.location.pathname;

    if (path.startsWith("/files")) {
        path = path.replace("/files", "");
    }

    return path.replace(/^\/+/, "");
}

async function getDirectory(path) {
    const url = path ? `/api/files/${path}` : "/api/files";

    const response = await fetch(url);
    const data = await response.json();

    return data;
}

async function loadIcon(path) {
    if (iconCache.has(path)) {
        return;
    }

    const response = await fetch(path);
    const svgText = await response.text();

    const container = document.createElement("div");
    container.innerHTML = svgText;

    const svg = container.firstElementChild;

    iconCache.set(path, svg);
}

function getIcon(path) {
    const svg = iconCache.get(path);

    return svg.cloneNode(true);
}

function renderBreadcrumb(path) {
    breadcrumb.innerHTML = "";

    const home = document.createElement("a");
    const fragment = document.createDocumentFragment();

    home.textContent = "Home";
    home.href = "/files";

    home.addEventListener("click", (event) => {
        event.preventDefault();

        history.pushState({}, "", "/files");
        showDirectory("");
    });

    fragment.appendChild(home);

    const parts = path ? path.split("/") : [];

    for (let i = 0; i < parts.length; i++) {
        const separator = document.createTextNode(" / ");
        fragment.appendChild(separator);

        const link = document.createElement("a");
        link.textContent = parts[i];

        const linkPath = parts.slice(0, i + 1).join("/");

        link.href = `/files/${linkPath}`;

        link.addEventListener("click", (event) => {
            event.preventDefault();

            history.pushState({}, "", `/files/${linkPath}`);
            showDirectory(linkPath);
        });

        fragment.appendChild(link);
    }

    breadcrumb.appendChild(fragment)
}

function renderDirectory(data) {
    files.innerHTML = "";
    
    const currentPath = getCurrentPath();

    const fragment = document.createDocumentFragment();

    if (currentPath !== "") {
        const parentLink = document.createElement("a");
        parentLink.textContent = "..";

        const parentPath = currentPath.split("/");
        parentPath.pop();

        const parent = parentPath.join("/");

        parentLink.href = `/files/${parent}`;

        parentLink.addEventListener("click", (event) => {
            event.preventDefault();

            history.pushState({}, "", `/files/${parent}`);

            showDirectory(parent);
        });

        fragment.appendChild(parentLink);
    }

    for (const item of data) {
        const link = document.createElement("a");
        const name = document.createElement("span");

        name.textContent = item.name;

        let icon;

        if (item.type === "file") {
            icon = getIcon(fileIconPath);
            link.href = `/view/${item.path}`;
        }
        else if (item.type === "directory") {
            icon = getIcon(directoryIconPath);
            link.href = `/files/${item.path}`;

            link.addEventListener("click", (event) => {
                event.preventDefault();

                history.pushState({}, "", `/files/${item.path}`);
                showDirectory(item.path);
            });
        }

        link.appendChild(icon);
        link.appendChild(name);

        fragment.appendChild(link);
    }

    files.appendChild(fragment);
}

async function showDirectory(path) {
    renderBreadcrumb(path);

    const data = await getDirectory(path);

    renderDirectory(data);
}

window.addEventListener("popstate", () => {
    const path = getCurrentPath();
    
    showDirectory(path);
});

async function init() {
    await loadIcon(fileIconPath);
    await loadIcon(directoryIconPath);

    showDirectory(getCurrentPath());
}

init();
