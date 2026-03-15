export function setStatus(element, message, type = "") {
  if (!element) {
    return;
  }
  element.textContent = message;
  element.className = `status ${type}`.trim();
}

export function toggleLoading(button, loadingText, defaultText, isLoading) {
  if (!button) {
    return;
  }

  button.disabled = isLoading;
  button.textContent = isLoading ? loadingText : defaultText;
}

export function setActiveNav(pathname) {
  const links = document.querySelectorAll(".nav a");
  links.forEach((link) => {
    const isActive = link.getAttribute("href").endsWith(pathname);
    link.classList.toggle("active", isActive);
  });
}

export function formatPercent(value) {
  return `${(Number(value) * 100).toFixed(2)}%`;
}
