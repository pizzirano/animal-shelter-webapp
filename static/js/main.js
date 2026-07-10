/* main.js — Dark mode, hamburger menu, FAQ accordion, reveal on scroll,
   scroll-to-top, gallery. */

document.addEventListener('DOMContentLoaded', function () {

  /* --- Dark Mode Toggle --- */
  var htmlEl  = document.documentElement;
  var themeBtn = document.querySelector('[data-theme-toggle]');
  var sunIcon  = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="5"/><path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/></svg>';
  var moonIcon = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>';

  if (themeBtn) {
    var currentTheme = htmlEl.getAttribute('data-theme') || 'light';
    themeBtn.innerHTML = currentTheme === 'dark' ? sunIcon : moonIcon;

    themeBtn.addEventListener('click', function () {
      currentTheme = currentTheme === 'dark' ? 'light' : 'dark';
      htmlEl.setAttribute('data-theme', currentTheme);
      localStorage.setItem('theme', currentTheme);
      themeBtn.innerHTML = currentTheme === 'dark' ? sunIcon : moonIcon;
    });
  }

  /* --- Hamburger Menu --- */
  const toggle = document.getElementById('navToggle');
  const menu   = document.getElementById('navMenu');

  if (toggle && menu) {
    toggle.addEventListener('click', function () {
      const isOpen = menu.classList.toggle('is-open');
      toggle.classList.toggle('is-open', isOpen);
      toggle.setAttribute('aria-expanded', String(isOpen));
    });

    document.addEventListener('click', function (e) {
      if (!toggle.contains(e.target) && !menu.contains(e.target)) {
        menu.classList.remove('is-open');
        toggle.classList.remove('is-open');
        toggle.setAttribute('aria-expanded', 'false');
      }
    });
  }

  /* --- FAQ Accordion --- */
  document.querySelectorAll('.faq-question').forEach(function (question) {
    question.addEventListener('click', function () {
      const item   = this.closest('.faq-item');
      const answer = item.querySelector('.faq-answer');
      const isOpen = item.classList.contains('is-open');

      /* Chiudi tutti */
      document.querySelectorAll('.faq-item.is-open').forEach(function (open) {
        open.classList.remove('is-open');
        open.querySelector('.faq-answer').style.maxHeight = '0';
      });

      /* Apri quello cliccato se era chiuso */
      if (!isOpen) {
        item.classList.add('is-open');
        answer.style.maxHeight = answer.scrollHeight + 'px';
      }
    });
  });

  /* Inizializza accordion (chiusi al caricamento) */
  document.querySelectorAll('.faq-answer').forEach(function (a) {
    a.style.maxHeight = '0';
  });

  /* --- IntersectionObserver: Reveal on scroll --- */
  var reveals = document.querySelectorAll('.reveal');
  if (reveals.length) {
    if ('IntersectionObserver' in window) {
      var observer = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            entry.target.classList.add('visible');
            observer.unobserve(entry.target);
          }
        });
      }, { threshold: 0.1, rootMargin: '0px 0px -36px 0px' });

      reveals.forEach(function (el) { observer.observe(el); });
    } else {
      /* Fallback: mostra subito su browser senza IntersectionObserver */
      reveals.forEach(function (el) { el.classList.add('visible'); });
    }
  }

  /* --- Scroll to Top --- */
  var scrollBtn = document.getElementById('scrollTop');
  if (scrollBtn) {
    window.addEventListener('scroll', function () {
      scrollBtn.classList.toggle('visible', window.scrollY > 300);
    }, { passive: true });

    scrollBtn.addEventListener('click', function () {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
  }

  /* --- Gallery cane: click su thumbnail --- */
  var mainImg = document.getElementById('mainDogImage');
  document.querySelectorAll('.dog-gallery__thumb').forEach(function (thumb) {
    thumb.addEventListener('click', function () {
      if (!mainImg) return;
      mainImg.src = this.dataset.src;
      mainImg.alt = this.dataset.alt || '';
      document.querySelectorAll('.dog-gallery__thumb').forEach(function (t) {
        t.classList.remove('active');
      });
      this.classList.add('active');
    });
  });

  /* --- Gallery cane: swipe touch --- */
  var galleryMain = document.querySelector('.dog-gallery__main');
  if (galleryMain && mainImg) {
    var touchStartX = 0;
    galleryMain.addEventListener('touchstart', function (e) {
      touchStartX = e.touches[0].clientX;
    }, { passive: true });

    galleryMain.addEventListener('touchend', function (e) {
      var delta = e.changedTouches[0].clientX - touchStartX;
      if (Math.abs(delta) < 40) return;
      var thumbs = Array.from(document.querySelectorAll('.dog-gallery__thumb'));
      if (!thumbs.length) return;
      var activeIdx = thumbs.findIndex(function (t) { return t.classList.contains('active'); });
      var nextIdx = delta < 0
        ? Math.min(activeIdx + 1, thumbs.length - 1)
        : Math.max(activeIdx - 1, 0);
      if (nextIdx !== activeIdx) thumbs[nextIdx].click();
    }, { passive: true });
  }

  /* --- Hero Carousel --- */
  var heroSlides = document.querySelectorAll('.hero__slide');
  var heroDots   = document.querySelectorAll('.hero__dot');
  var heroIdx    = 0;
  var heroTimer  = null;
  var heroPaused = false;

  function heroGoTo(n) {
    heroSlides[heroIdx].classList.remove('is-active');
    heroDots[heroIdx].classList.remove('is-active');
    heroDots[heroIdx].setAttribute('aria-selected', 'false');
    heroIdx = (n + heroSlides.length) % heroSlides.length;
    heroSlides[heroIdx].classList.add('is-active');
    heroDots[heroIdx].classList.add('is-active');
    heroDots[heroIdx].setAttribute('aria-selected', 'true');
  }

  function heroNext() { if (!heroPaused) heroGoTo(heroIdx + 1); }

  if (heroSlides.length > 1) {
    heroTimer = setInterval(heroNext, 5000);

    heroDots.forEach(function (dot, i) {
      dot.addEventListener('click', function () {
        heroGoTo(i);
        clearInterval(heroTimer);
        heroTimer = setInterval(heroNext, 5000);
      });
    });

    var heroSection = document.getElementById('heroSection');
    if (heroSection) {
      heroSection.addEventListener('mouseenter', function () { heroPaused = true; });
      heroSection.addEventListener('mouseleave', function () { heroPaused = false; });
    }
  }

});
