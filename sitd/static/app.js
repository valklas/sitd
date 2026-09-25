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
    const response= await fetch(`/api/files/${path}`);
    const data = await response.json();

    return data;
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

function renderDirectory(data) {
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
        files.appendChild(document.createElement("br"));
    }

    for (const item of data) {
        const link = document.createElement("a");
        link.textContent = item.name;

        if (item.type == "file") {
            link.href = `/files/${item.path}`;
        }
        else if (item.type == "directory") {
            link.href = `/files/${item.path}`;

            link.addEventListener("click", (event) => {
                event.preventDefault();

                history.pushState({}, "", `/files/${item.path}`);

                showDirectory(item.path);
            });
        }

        files.appendChild(link);
        files.appendChild(document.createElement("br"));
    }
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

showDirectory(getCurrentPath());
