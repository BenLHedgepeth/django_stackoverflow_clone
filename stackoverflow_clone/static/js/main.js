
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


window.addEventListener("DOMContentLoaded", function(event) {
  const current_url = `${window.location}`;
  const url = new URL(current_url);
  if (url.pathname.endsWith("/search/")) {
    if (url.href.endsWith("/search/")) {
      return
    }
    const invalid_query = new RegExp(/^\?(?!q=)\//);
    if (invalid_query.test(url.search)) {
      window.location = `${url.pathname}?q=`;
    } else {
      //pass
    }
  }
  return
})
