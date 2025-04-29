import { codeToHtml } from "https://esm.sh/shiki@3.0.0";
const handleNode = async (node) => {
  // Handle the newly created node
  console.log("Node created:", node);
  if (node.nodeName === "CODE") {
    let lang =
      node.getAttribute("lang");
    if (!lang){
      const index = Array.from(node.classList).findIndex((value) =>
        value.startsWith("language-")
      )
      if (index == -1){
        console.log("Code has no language", Array.from(node.classList))
        return
      }else{
        lang =       node.classList[
          Array.from(node.classList).findIndex((value) =>
            value.startsWith("language-")
          )
        ].slice("language-".length);
      }
    }

    node.innerHTML = await codeToHtml(node.innerText, {
      lang,
      theme: "github-dark",
    });
  } else {
    Array.prototype.forEach.call(node.childNodes,handleNode);
  }
};
Array.from(document.getElementsByTagName("code")).forEach(handleNode);
const observer = new MutationObserver((mutations) => {
  mutations.forEach((mutation) => {
    if (mutation.type === "childList") {
      mutation.addedNodes.forEach(handleNode);
    }
  });
});

// Start observing the document or a specific element
observer.observe(document.body, {
  childList: true, // Listen for addition/removal of child nodes
  subtree: true, // Listen for changes in all descendants
});
