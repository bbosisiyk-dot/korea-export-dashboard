    (() => {
      const tooltip = document.getElementById("chart-tooltip");
      if (!tooltip) return;

      function moveTooltip(event) {
        const target = event.target instanceof Element ? event.target.closest("[data-tooltip]") : null;
        if (!target) {
          tooltip.classList.remove("is-visible");
          return;
        }

        tooltip.textContent = target.getAttribute("data-tooltip") || "";
        tooltip.style.left = event.clientX + "px";
        tooltip.style.top = (event.clientY - 12) + "px";
        tooltip.classList.add("is-visible");

        const padding = 12;
        const rect = tooltip.getBoundingClientRect();
        let left = event.clientX;
        let top = event.clientY - 12;
        if (rect.right > window.innerWidth - padding) left -= rect.right - window.innerWidth + padding;
        if (rect.left < padding) left += padding - rect.left;
        if (rect.top < padding) top = event.clientY + rect.height + 18;
        tooltip.style.left = left + "px";
        tooltip.style.top = top + "px";
      }

      document.addEventListener("pointermove", moveTooltip);
      document.addEventListener("pointerleave", () => tooltip.classList.remove("is-visible"));
      document.addEventListener("scroll", () => tooltip.classList.remove("is-visible"), true);
    })();
  
