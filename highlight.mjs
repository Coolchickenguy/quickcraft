// be sure to specify the exact version
import { codeToHtml } from "https://esm.sh/shiki@3.0.0";
// or
// import { codeToHtml } from 'https://esm.run/shiki@3.0.0'
const handleNode = async (node) => {
  // Handle the newly created node
  console.log("Node created:", node);
  // Add your logic here, e.g., add event listeners, modify content, etc.
  if (node.nodeName === "CODE") {
    node.innerHTML = await codeToHtml(node.innerText, {
      lang: node.getAttribute("lang"),
      theme: "github-dark",
    });
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
