(() => {
  const button = document.querySelector('.menu-button');
  const nav = document.querySelector('.primary-nav');

  if (button && nav) {
    button.addEventListener('click', () => {
      const open = nav.classList.toggle('open');
      button.setAttribute('aria-expanded', String(open));
      button.textContent = open ? 'Close' : 'Menu';
    });

    nav.querySelectorAll('a').forEach(link => {
      link.addEventListener('click', () => {
        nav.classList.remove('open');
        button.setAttribute('aria-expanded', 'false');
        button.textContent = 'Menu';
      });
    });
  }

  const lightbox = document.querySelector('.lightbox');
  if (!lightbox) return;

  const lightboxImage = lightbox.querySelector('img');
  const lightboxCaption = lightbox.querySelector('p');
  const closeButton = lightbox.querySelector('button');

  function closeLightbox() {
    lightbox.hidden = true;
    lightbox.setAttribute('aria-hidden', 'true');
    lightboxImage.removeAttribute('src');
    document.body.style.overflow = '';
  }

  document.querySelectorAll('[data-lightbox]').forEach(image => {
    image.addEventListener('click', () => {
      lightboxImage.src = image.currentSrc || image.src;
      lightboxImage.alt = image.alt || '';
      const figure = image.closest('figure');
      const caption = figure?.querySelector('figcaption');
      lightboxCaption.textContent = caption ? caption.textContent.trim() : '';
      lightbox.hidden = false;
      lightbox.setAttribute('aria-hidden', 'false');
      document.body.style.overflow = 'hidden';
      closeButton.focus();
    });
  });

  closeButton.addEventListener('click', closeLightbox);
  lightbox.addEventListener('click', event => {
    if (event.target === lightbox) closeLightbox();
  });

  document.addEventListener('keydown', event => {
    if (event.key === 'Escape' && !lightbox.hidden) closeLightbox();
  });
})();

/* SITE-DROPDOWN-NAV:START */
(() => {
  const header = document.querySelector('.site-header.fieldstation-header');
  const button = document.querySelector('.field-index-button');
  const panel = document.querySelector('.field-index-panel');

  if (!header || !button || !panel) return;

  function closeIndex() {
    header.classList.remove('index-open');
    button.setAttribute('aria-expanded', 'false');
    button.textContent = 'Field Index';
  }

  function openIndex() {
    header.classList.add('index-open');
    button.setAttribute('aria-expanded', 'true');
    button.textContent = 'Close Index';
  }

  button.addEventListener('click', event => {
    event.preventDefault();
    const open = header.classList.contains('index-open');
    if (open) closeIndex();
    else openIndex();
  });

  panel.querySelectorAll('a').forEach(link => {
    link.addEventListener('click', closeIndex);
  });

  document.addEventListener('click', event => {
    if (!header.contains(event.target)) closeIndex();
  });

  document.addEventListener('keydown', event => {
    if (event.key === 'Escape') closeIndex();
  });
})();
/* SITE-DROPDOWN-NAV:END */
