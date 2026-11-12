// Theme switch: follows the system until you press the button, then remembers your choice.
(function () {
  const root = document.documentElement;
  const btn = document.querySelector(".theme");
  if (btn) {
    btn.addEventListener("click", () => {
      const dark = root.dataset.theme
        ? root.dataset.theme === "dark"
        : window.matchMedia("(prefers-color-scheme: dark)").matches;
      root.dataset.theme = dark ? "light" : "dark";
      try { localStorage.setItem("theme", root.dataset.theme); } catch (e) {}
    });
  }

  // Photo lightbox: click a photo to see it large, click again or press Esc to close.
  const box = document.querySelector(".lightbox");
  if (!box) return;
  const big = box.querySelector("img");
  const cap = box.querySelector("p");
  document.querySelectorAll(".gallery img").forEach((img) => {
    img.addEventListener("click", () => {
      big.src = img.dataset.full || img.src;
      big.alt = img.alt;
      const fc = img.closest("figure").querySelector("figcaption");
      cap.textContent = fc ? fc.textContent : "";
      box.hidden = false;
    });
  });
  const close = () => { box.hidden = true; big.removeAttribute("src"); };
  box.addEventListener("click", close);
  document.addEventListener("keydown", (e) => { if (e.key === "Escape") close(); });
})();
