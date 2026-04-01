document.addEventListener("DOMContentLoaded", () => {
  // Loader
  const loader = document.getElementById("appLoader");
  setTimeout(() => loader?.classList.add("hide"), 900);

  // Theme toggle
  const root = document.documentElement;
  const themeToggle = document.getElementById("themeToggle");
  const themeLabel = document.getElementById("themeLabel");
  const themeIcon = document.getElementById("themeIcon");
  const savedTheme = localStorage.getItem("theme") || "dark";
  root.setAttribute("data-theme", savedTheme);

  function updateThemeButton(theme) {
    if (!themeLabel) return;
    if (theme === "dark") {
      themeLabel.textContent = "Dark Mode";
      if (themeIcon) themeIcon.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>`;
    } else {
      themeLabel.textContent = "Light Mode";
      if (themeIcon) themeIcon.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/></svg>`;
    }
  }

  updateThemeButton(savedTheme);

  themeToggle?.addEventListener("click", () => {
    const next = root.getAttribute("data-theme") === "dark" ? "light" : "dark";
    root.setAttribute("data-theme", next);
    localStorage.setItem("theme", next);
    updateThemeButton(next);
    pushToast(`Theme changed to ${next}`);
  });

  // Sidebar collapse
  const sidebar = document.getElementById("sidebar");
  const sidebarBtn = document.getElementById("sidebarToggle");
  const pageRoot = document.getElementById("pageRoot");
  const collapsed = localStorage.getItem("sidebar-collapsed") === "1";
  if (collapsed && sidebar) {
    sidebar.classList.add("collapsed");
    pageRoot?.classList.add("sidebar-collapsed");
  }

  sidebarBtn?.addEventListener("click", () => {
    sidebar?.classList.toggle("collapsed");
    const isNowCollapsed = sidebar?.classList.contains("collapsed");
    pageRoot?.classList.toggle("sidebar-collapsed", isNowCollapsed);
    localStorage.setItem("sidebar-collapsed", isNowCollapsed ? "1" : "0");
  });

  // Auto remove flash + mirror as toast
  document.querySelectorAll(".flash").forEach((f, i) => {
    setTimeout(() => pushToast(f.textContent.trim()), 200 + i * 120);
    setTimeout(() => {
      f.style.transition = ".4s";
      f.style.opacity = "0";
      f.style.transform = "translateY(-4px)";
      setTimeout(() => f.remove(), 380);
    }, 2600);
  });

  // Reusable confirm modal for delete forms
  const modal = document.getElementById("globalModal");
  const cancelBtn = document.getElementById("modalCancel");
  const confirmBtn = document.getElementById("modalConfirm");
  let formToSubmit = null;

  document.querySelectorAll(".delete-form").forEach((form) => {
    form.addEventListener("submit", (e) => {
      e.preventDefault();
      formToSubmit = form;
      openModal("Delete Record", "This action cannot be undone. Are you sure?");
    });
  });

  cancelBtn?.addEventListener("click", closeModal);
  confirmBtn?.addEventListener("click", () => {
    if (formToSubmit) formToSubmit.submit();
    closeModal();
  });
  modal?.addEventListener("click", (e) => {
    if (e.target === modal) closeModal();
  });

  function openModal(title, message) {
    document.getElementById("modalTitle").textContent = title;
    document.getElementById("modalMessage").textContent = message;
    modal?.classList.add("show");
  }
  function closeModal() {
    modal?.classList.remove("show");
    formToSubmit = null;
  }

  // Ripple buttons
  document.querySelectorAll(".ripple").forEach((btn) => {
    btn.addEventListener("click", function (e) {
      const wave = document.createElement("span");
      wave.classList.add("ripple-wave");
      const rect = btn.getBoundingClientRect();
      const size = Math.max(rect.width, rect.height);
      wave.style.width = wave.style.height = size + "px";
      wave.style.left = e.clientX - rect.left - size / 2 + "px";
      wave.style.top = e.clientY - rect.top - size / 2 + "px";
      btn.appendChild(wave);
      setTimeout(() => wave.remove(), 650);
    });
  });

  // Chart (if present)
  const chartCanvas = document.getElementById("statusChart");
  if (chartCanvas) {
    const labels = JSON.parse(chartCanvas.dataset.labels || "[]");
    const values = JSON.parse(chartCanvas.dataset.values || "[]");
    new Chart(chartCanvas, {
      type: "doughnut",
      data: {
        labels,
        datasets: [{ data: values, backgroundColor: ["#3b82f6", "#10b981", "#ef4444"], borderWidth: 0 }]
      },
      options: {
        plugins: { legend: { labels: { color: getComputedStyle(document.body).color } } }
      }
    });
  }

  // ----- Table sorting -----
  document.querySelectorAll(".sortable-th").forEach((th) => {
    th.addEventListener("click", () => {
      const table = th.closest("table");
      const tbody = table.querySelector("tbody");
      const colIdx = Array.from(th.parentElement.children).indexOf(th);
      const asc = th.classList.toggle("sort-asc");
      th.classList.toggle("sort-desc", !asc);

      // Clear siblings
      th.parentElement.querySelectorAll(".sortable-th").forEach((s) => {
        if (s !== th) { s.classList.remove("sort-asc", "sort-desc"); }
      });

      const rows = Array.from(tbody.querySelectorAll("tr"));
      rows.sort((a, b) => {
        const aText = (a.cells[colIdx]?.textContent || "").trim();
        const bText = (b.cells[colIdx]?.textContent || "").trim();
        const aNum = parseFloat(aText);
        const bNum = parseFloat(bText);
        if (!isNaN(aNum) && !isNaN(bNum)) return asc ? aNum - bNum : bNum - aNum;
        return asc ? aText.localeCompare(bText) : bText.localeCompare(aText);
      });
      rows.forEach((r) => tbody.appendChild(r));
    });
  });

  // ----- Day picker (multi-select) -----
  document.querySelectorAll(".day-picker").forEach((picker) => {
    const toggle = picker.querySelector(".day-picker-toggle");
    const dropdown = picker.querySelector(".day-picker-dropdown");
    const checkboxes = picker.querySelectorAll("input[type=checkbox]");
    const display = picker.querySelector(".day-picker-selected");

    function refreshDisplay() {
      const selected = Array.from(checkboxes)
        .filter((c) => c.checked)
        .map((c) => c.value);
      if (display) {
        display.innerHTML = selected.length
          ? selected.map((d) => `<span class="day-chip">${d}</span>`).join("")
          : '<span style="color:var(--muted)">No days selected</span>';
      }
      const label = selected.length ? selected.join(", ") : "Select days…";
      toggle.firstChild.textContent = label;
    }

    toggle?.addEventListener("click", (e) => {
      e.preventDefault();
      toggle.classList.toggle("open");
      dropdown?.classList.toggle("open");
    });

    checkboxes.forEach((cb) => cb.addEventListener("change", refreshDisplay));

    // Close when clicking outside
    document.addEventListener("click", (e) => {
      if (!picker.contains(e.target)) {
        toggle?.classList.remove("open");
        dropdown?.classList.remove("open");
      }
    });

    refreshDisplay();
  });

  // Password eye toggle
  document.querySelectorAll(".pwd-eye").forEach((btn) => {
    btn.addEventListener("click", () => {
      const input = btn.parentElement.querySelector("input");
      if (!input) return;
      const isShown = btn.classList.toggle("shown");
      input.type = isShown ? "text" : "password";
    });
  });

  function pushToast(message) {
    const holder = document.getElementById("toastContainer");
    if (!holder || !message) return;
    const toast = document.createElement("div");
    toast.className = "toast";
    toast.textContent = message;
    holder.appendChild(toast);
    setTimeout(() => {
      toast.style.opacity = "0";
      toast.style.transform = "translateX(12px)";
      toast.style.transition = ".35s";
      setTimeout(() => toast.remove(), 350);
    }, 2600);
  }
});