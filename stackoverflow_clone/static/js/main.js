
// alert(window.scrollY);
//
//
// document.addEventListener("scroll", (e) => {
//   if (window.pageYOffset >= screen_body.clientHeight)
// })

var search_form = document.querySelector("#id_q");
search_form.addEventListener("focus", function(event) {
  let search_menu_help = document.querySelector("#help_menu");
  search_menu_help.classList.remove("hide_menu");
  search_menu_help.classList.add("show_menu");
})

search_form.addEventListener("blur", function(event) {
  let search_menu_help = document.querySelector("#help_menu");
  search_menu_help.classList.remove("show_menu");
  search_menu_help.classList.add("hide_menu");
})


const page_container = document.querySelector("body");

// console.log(window.innerHeight + page_container.offsetHeight);
const page_container_height = page_container.offsetHeight;
page_container.style.paddingBottom = `125px`;
