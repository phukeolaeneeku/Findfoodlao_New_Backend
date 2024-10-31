function setScreenSize() {
  let vh = window.innerHeight * 0.01;
  document.documentElement.style.setProperty("--vh", `${vh}px`);
}
setScreenSize();
window.addEventListener("resize", setScreenSize);

function disableScroll() {
  document.querySelector("body").addEventListener("touchmove", removeEvent, {
    passive: false,
  });
  document.querySelector("body").addEventListener("click", removeEvent, {
    passive: false,
  });
  document.querySelector("body").addEventListener("mousewheel", removeEvent, {
    passive: false,
  });
}

function removeEvent(e) {
  e.preventDefault();
  e.stopPropagation();
}

function enableScroll() {
  document.querySelector("body").removeEventListener("touchmove", removeEvent);
  document.querySelector("body").removeEventListener("click", removeEvent);
  document.querySelector("body").removeEventListener("mousewheel", removeEvent);
}

function goBack() {
  window.history.back();
}

$(function () {
  $(".tabcontent > div").hide();
  $(".tabnav a.link")
    .click(function () {
      $(".tabcontent > div").hide().filter(this.hash).fadeIn();
      $(".tabnav a.link").removeClass("active");
      $(this).addClass("active");
      return false;
    })
    .filter(":eq(0)")
    .click();
});

$(".drop_box > ul > li > a").click(function () {
  $(this).parent("li").toggleClass("on");
  $(this).parent("li").siblings().removeClass("on");
  $(this).toggleClass("active").next("div").slideToggle(200);
  $(this).parent().siblings().children("div").slideUp(200);
  $(this).parent().siblings().children(".active").removeClass("active");
  return false;
});
