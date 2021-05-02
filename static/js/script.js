$(function () {
  $('[data-toggle="popover"]').popover()
})

function showLoadingScreen() {
  var overlay = document.getElementById("overlay");
  if (overlay) {
    overlay.style.display = "initial";
  }
}

function hideLoadingScreen() {
  var overlay = document.getElementById("overlay");
  if (overlay) {
    overlay.style.display = "none";
  }
}
