const resourceLinkCont = document.getElementById("resource_link_cont");
const resourceLinkChildren = Array.from(resourceLinkCont.children).map(child =>
                                                                    child.href);

const resourceContainer = document.getElementById("id_resources");
const resourceLabels = resourceContainer.getElementsByTagName("label");

const resourceNames = Array.from(resourceLabels).map(label => {
    const name = label.textContent;
    changeLabelText(label, ""); // Clear the label text
    return name;
});

function changeLabelText(label, text) {
    Array.from(label.childNodes).forEach(child => {
        if (child.nodeType === Node.TEXT_NODE) {
            child.textContent = text;
        }
    });
}

resourceNames.forEach((name, index) => {
    const newLink = document.createElement("a");
    newLink.href = resourceLinkChildren[index];
    newLink.textContent = name;
    newLink.target = "_blank";
    resourceLabels[index].appendChild(newLink);
});
