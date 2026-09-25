const breadcrumb = document.getElementById("breadcrumb");
const files = document.getElementById("files");

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
    const response = await fetch(path);
    const svgText = await response.text();

    const container = document.createElement("div");
    container.innerHTML = svgText;

    return container.firstElementChild;
}

function renderBreadcrumb(path) {
    breadcrumb.innerHTML = "";

    const home = document.createElement("a");

    home.textContent = "Home";
    home.href = "/files";

    home.addEventListener("click", (event) => {
        event.preventDefault();

        history.pushState({}, "", "/files");
        showDirectory("");
    });

    breadcrumb.appendChild(home);

    const parts = path ? path.split("/") : [];

    for (let i = 0; i < parts.length; i++) {
        const separator = document.createTextNode(" / ");
        breadcrumb.appendChild(separator);

        const link = document.createElement("a");
        link.textContent = parts[i];

        const linkPath = parts.slice(0, i + 1).join("/");

        link.href = `/files/${linkPath}`;

        link.addEventListener("click", (event) => {
            event.preventDefault();

            history.pushState({}, "", `/files/${linkPath}`);
            showDirectory(linkPath);
        });

        breadcrumb.appendChild(link);
    }
}

async function renderDirectory(data) {
    files.innerHTML = "";
    
    const currentPath = getCurrentPath();

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

        files.appendChild(parentLink);
    }

    for (const item of data) {
        const link = document.createElement("a");
        const name = document.createElement("span");

        link.href = `/files/${item.path}`;
        name.textContent = item.name;

        let icon;

        if (item.type === "file") {
            icon = await loadIcon(
                "/static/assets/icons/white/file-white-24.svg"
            );
        }
        else if (item.type === "directory") {
            icon = await loadIcon(
                "/static/assets/icons/white/file-directory-fill-white-24.svg"
            );

            link.addEventListener("click", (event) => {
                event.preventDefault();

                history.pushState({}, "", `/files/${item.path}`);
                showDirectory(item.path);
            });
        }

        link.appendChild(icon);
        link.appendChild(name);

        files.appendChild(link);
    }
}

async function showDirectory(path) {
    renderBreadcrumb(path);

    const data = await getDirectory(path);

    await renderDirectory(data);
}

window.addEventListener("popstate", () => {
    const path = getCurrentPath();
    
    showDirectory(path);
});

showDirectory(getCurrentPath());
