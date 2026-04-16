document.addEventListener('DOMContentLoaded', () => {

  // ==================== THEME TOGGLE ====================
  const btns = [document.getElementById('theme-btn'), document.getElementById('theme-btn-mobile')].filter(Boolean);
  const saved = localStorage.getItem('theme') || 'light';
  document.documentElement.setAttribute('data-theme', saved);
  btns.forEach(b => b.textContent = saved === 'dark' ? '\u2600' : '\u263D');

  btns.forEach(btn => {
    btn.addEventListener('click', () => {
      const next = document.documentElement.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
      document.documentElement.setAttribute('data-theme', next);
      localStorage.setItem('theme', next);
      btns.forEach(b => b.textContent = next === 'dark' ? '\u2600' : '\u263D');
    });
  });

  // ==================== SPA-STYLE NAVIGATION (NO PAGE RELOAD) ====================
  // Intercept internal link clicks, fetch new page via AJAX, swap <main> content
  // This eliminates the white flash entirely because the page is never destroyed

  function isInternalLink(a) {
    if (!a || !a.href) return false;
    if (a.hasAttribute('download')) return false;
    if (a.href.endsWith('.pdf')) return false;
    if (a.target === '_blank') return false;
    if (a.href.startsWith('mailto:') || a.href.startsWith('tel:')) return false;
    try {
      const url = new URL(a.href);
      return url.origin === window.location.origin;
    } catch { return false; }
  }

  async function navigateTo(url, pushState = true) {
    try {
      const res = await fetch(url);
      if (!res.ok) { window.location.href = url; return; }
      const html = await res.text();
      const parser = new DOMParser();
      const doc = parser.parseFromString(html, 'text/html');

      // Swap main content
      const newMain = doc.querySelector('main');
      const oldMain = document.querySelector('main');
      if (newMain && oldMain) {
        oldMain.innerHTML = newMain.innerHTML;
      }

      // Update page title
      document.title = doc.title;

      // Update active nav link
      updateActiveNav(url);

      // Push to browser history
      if (pushState) {
        history.pushState({}, '', url);
      }

      // Scroll to top
      window.scrollTo({ top: 0, behavior: 'instant' });

      // Re-run reveal animations for new content
      initReveals();

      // Re-run typing animation if on home page
      initTyping();

    } catch (e) {
      // Fallback to normal navigation on error
      window.location.href = url;
    }
  }

  // Handle back/forward browser buttons
  window.addEventListener('popstate', () => {
    navigateTo(window.location.href, false);
  });

  // Intercept all internal link clicks (skip downloads and PDFs)
  document.addEventListener('click', (e) => {
    const a = e.target.closest('a');
    if (!a) return;
    // Let the browser handle download links and PDFs natively
    if (a.hasAttribute('download') || a.href.endsWith('.pdf')) return;
    if (a && isInternalLink(a)) {
      e.preventDefault();
      navigateTo(a.href);
    }
  });

  function updateActiveNav(url) {
    const path = new URL(url).pathname;
    document.querySelectorAll('.nav-links a').forEach(a => {
      a.classList.remove('active');
      const href = a.getAttribute('href');
      if (!href) return;
      // Skip resume download link
      if (a.classList.contains('nav-resume')) return;
      if (path === href || (href !== '/' && path.startsWith(href))) {
        a.classList.add('active');
      }
    });
  }

  // ==================== SCROLL REVEAL ====================
  function initReveals() {
    const allReveals = document.querySelectorAll('.reveal, .stagger-children');

    // Mark above-fold elements as immediately visible
    allReveals.forEach(el => {
      el.classList.remove('visible');
      const rect = el.getBoundingClientRect();
      if (rect.top < window.innerHeight + 50) {
        el.classList.add('visible');
      }
    });

    // Enable animation class
    document.body.classList.add('reveal-ready');

    // Observe below-fold elements
    const obs = new IntersectionObserver((entries) => {
      entries.forEach(e => {
        if (e.isIntersecting) {
          e.target.classList.add('visible');
        }
      });
    }, { threshold: 0.08, rootMargin: '0px 0px -40px 0px' });

    allReveals.forEach(el => {
      if (!el.classList.contains('visible')) {
        obs.observe(el);
      }
    });
  }

  // ==================== TYPING ANIMATION ====================
  function initTyping() {
    const typingEl = document.getElementById('hero-typing');
    if (typingEl) {
      const text = typingEl.getAttribute('data-text');
      typingEl.textContent = '';
      let i = 0;
      const typeInterval = setInterval(() => {
        if (i < text.length) {
          typingEl.textContent += text.charAt(i);
          i++;
        } else {
          clearInterval(typeInterval);
        }
      }, 65);
    }
  }

  // ==================== NAVBAR SCROLL SHADOW ====================
  const navbar = document.querySelector('.navbar');
  if (navbar) {
    let ticking = false;
    window.addEventListener('scroll', () => {
      if (!ticking) {
        window.requestAnimationFrame(() => {
          navbar.style.boxShadow = window.scrollY > 20 ? 'var(--shadow-sm)' : 'none';
          ticking = false;
        });
        ticking = true;
      }
    });
  }

  // ==================== MOBILE NAV ====================
  const ham = document.getElementById('hamburger');
  const nav = document.getElementById('nav-links');
  if (ham) {
    ham.addEventListener('click', () => {
      nav.classList.toggle('open');
      ham.textContent = nav.classList.contains('open') ? '\u2715' : '\u2630';
    });
  }

  // ==================== INIT ====================
  initReveals();
  initTyping();
});
