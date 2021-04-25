
const markdown_button = document.getElementById("md_helpbox");
const cancel = document.querySelector("#cancel_md");

markdown_button.addEventListener("click", function(event) {
  let markdown_menu = document.querySelector(".markdown_helper");
  markdown_menu.classList.toggle("hide")
})

cancel.addEventListener("click", function(event) {
  let markdown_menu = document.querySelector(".markdown_helper");
  markdown_menu.classList.toggle("hide")
})
