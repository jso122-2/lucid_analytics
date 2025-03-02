document.addEventListener("DOMContentLoaded", function () {
  // Simulate real-time data updates for dashboard cards using dummy JSON
  setInterval(function () {
    document.querySelectorAll(".card").forEach(card => {
      const randomValue = Math.floor(Math.random() * 100);
      const infoElem = card.querySelector(".card-front p");
      if (infoElem) {
        infoElem.innerText = "Updated: " + randomValue;
      }
    });
  }, 5000);

  // Animate dashboard cards on hover (adding a class for CSS transitions)
  document.addEventListener("mouseover", function (e) {
    const card = e.target.closest(".card");
    if (card) {
      card.classList.add("hovered");
    }
  });
  document.addEventListener("mouseout", function (e) {
    const card = e.target.closest(".card");
    if (card) {
      card.classList.remove("hovered");
    }
  });

  // Dark mode toggle logic with localStorage
  const darkModeToggle = document.getElementById("dark-mode-toggle");
  if (darkModeToggle) {
    if (localStorage.getItem("theme") === "dark") {
      document.body.classList.add("dark-mode");
      darkModeToggle.innerText = "Light Mode";
    }
    darkModeToggle.addEventListener("click", function () {
      document.body.classList.toggle("dark-mode");
      if (document.body.classList.contains("dark-mode")) {
        localStorage.setItem("theme", "dark");
        darkModeToggle.innerText = "Light Mode";
      } else {
        localStorage.setItem("theme", "light");
        darkModeToggle.innerText = "Dark Mode";
      }
    });
  }
});
