const files = document.getElementById("files");

async function getDirectory(path) {
    const responce = await fetch(`/api/files/${path}`);
    const data = await responce.json();

    return data;
}

function renderDirectory(data) {
    files.innerHTML = "";
    
    currentPath = getCurrentPath();

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

function getCurrentPath() {
    let path = window.location.pathname;

    if (path.startsWith("/files")) {
        path = path.replace("/files", "");
    }

    return path.replace(/^\/+/, "");
}

async function showDirectory(path) {
    const data = await getDirectory(path);

    renderDirectory(data);
}

window.addEventListener("popstate", () => {
    const path = getCurrentPath();
    
    showDirectory(path);
});

showDirectory(getCurrentPath());
