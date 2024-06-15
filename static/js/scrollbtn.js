window.onscroll = function() {scrollFunction()};

function scrollFunction() {
if (document.body.scrollTop > 40 || document.documentElement.scrollTop > 40) {
    document.getElementById("scrollToTopBtn").classList.add("show");
} else {
    document.getElementById("scrollToTopBtn").classList.remove("show");
}
}

document.getElementById("scrollToTopBtn").onclick = function() {
    scrollToTop();
};

function scrollToTop() {
    document.body.scrollTop = 0;
    document.documentElement.scrollTop = 0;
}
