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

function getIcon(path) {
    const svg = iconCache.get(path);

    return svg.cloneNode(true);
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

function humanReadable(bytes) {
    const units = ["B", "KB", "MB", "GB", "TB"];

    let size = bytes;
    let unit = 0;

    while (size >= 1024 && unit < units.length - 1) {
        size /= 1024;
        unit++;
    }

    return `${size.toFixed(2)} ${units[unit]}`;
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
            link.href = `/files/${item.path}`;
        
            link.addEventListener("click", (event) => {
                event.preventDefault();
        
                history.pushState({}, "", `/files/${item.path}`);
                showDirectory(item.path);
            });
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

async function renderFile(data) {
    files.innerHTML = "";

    const name = document.createElement("p");
    const fileType = document.createElement("p");
    const size = document.createElement("p");

    name.textContent = `Name: ${data.name}`;
    fileType.textContent = `Type: ${data.mime_type}`;
    size.textContent = `Size: ${humanReadable(data.file_size)}`;

    files.appendChild(name);
    files.appendChild(fileType);
    files.appendChild(size);

    if (data.mime_type === null) {
        const download = document.createElement("a");

        download.href = `/api/content/${data.path}`;
        download.textContent = "Download file";
        download.download = data.name;

        files.appendChild(download);

        return;
    }

    if (data.mime_type.startsWith("text/")) {
        const contentElement = document.createElement("pre");

        const response = await fetch(`/api/content/${data.path}`);
        const content = await response.text();

        contentElement.textContent = content;

        files.appendChild(contentElement);

        return;
    }

    if (data.mime_type.startsWith("image/")) {
        const image = document.createElement("img");

        image.src = `/api/content/${data.path}`;
        image.alt = data.name;

        files.appendChild(image);

        return;
    }

    if (data.mime_type.startsWith("video/")) {
        const video = document.createElement("video");

        video.src = `/api/content/${data.path}`;
        video.controls = true;

        files.appendChild(video);

        return;
    }

    if (data.mime_type.startsWith("audio/")) {
        const audio = document.createElement("audio");

        audio.src = `/api/content/${data.path}`;
        audio.controls = true;

        files.appendChild(audio);

        return;
    }

    const download = document.createElement("a");

    download.href = `/api/content/${data.path}`;
    download.textContent = "Download file";
    download.download = data.name;

    files.appendChild(download);
}

async function showDirectory(path) {
    renderBreadcrumb(path);

    const data = await getDirectory(path);

    if (Array.isArray(data)) {
        renderDirectory(data);
    }
    else {
        renderFile(data);
    }
}

window.addEventListener("popstate", () => {
    const path = getCurrentPath();
    
    showDirectory(path);
});

async function init() {
    await loadIcon(fileIconPath);
    await loadIcon(directoryIconPath);

    const path = getCurrentPath();

    showDirectory(path);
}

init();
