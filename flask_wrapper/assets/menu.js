var button = document.getElementById("close_menu")
var button_open = document.getElementById("open_menu")
var sidebar = document.getElementById("menubar");

button.addEventListener("click", function() {
    sidebar.style.display = "none";
});

button_open.addEventListener("click", function() {
    sidebar.style.display = "block";
})
