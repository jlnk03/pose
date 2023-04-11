//  Show menu outside dashboard

let button = document.getElementById("close_menu")
let button_open = document.getElementById("open_menu")
let sidebar = document.getElementById("menubar");

button.addEventListener("click", function () {
    sidebar.style.display = "none";
});

button_open.addEventListener("click", function () {
    sidebar.style.display = "block";
    // sidebar.style.transition = "opacity 0.5s";
})
