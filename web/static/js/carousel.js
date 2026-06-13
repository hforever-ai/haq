/* Aarambha Haq — Hero Carousel */
(function () {
  const carousel = document.getElementById('heroCarousel');
  if (!carousel) return;

  const slides = Array.from(carousel.querySelectorAll('.hero-slide'));
  const allDots = Array.from(carousel.querySelectorAll('.hero-dot'));
  const INTERVAL = 6000;
  let current = 0;
  let timer;

  function goTo(idx) {
    slides[current].classList.remove('is-active');
    allDots.forEach(d => { d.classList.remove('is-active'); d.setAttribute('aria-selected', 'false'); });

    current = (idx + slides.length) % slides.length;

    slides[current].classList.add('is-active');
    // sync all dot sets (each slide has its own dot row on mobile)
    carousel.querySelectorAll(`.hero-dot[data-index="${current}"]`).forEach(d => {
      d.classList.add('is-active');
      d.setAttribute('aria-selected', 'true');
    });
  }

  function next() { goTo(current + 1); }

  function startTimer() {
    clearInterval(timer);
    timer = setInterval(next, INTERVAL);
  }

  // Dot click
  allDots.forEach(dot => {
    dot.addEventListener('click', () => {
      goTo(parseInt(dot.dataset.index, 10));
      startTimer();
    });
  });

  // Pause on hover / touch
  carousel.addEventListener('mouseenter', () => clearInterval(timer));
  carousel.addEventListener('mouseleave', startTimer);

  // Touch swipe support
  let touchX = 0;
  carousel.addEventListener('touchstart', e => { touchX = e.touches[0].clientX; }, { passive: true });
  carousel.addEventListener('touchend', e => {
    const dx = e.changedTouches[0].clientX - touchX;
    if (Math.abs(dx) > 50) { goTo(current + (dx < 0 ? 1 : -1)); startTimer(); }
  }, { passive: true });

  // Pause when tab not visible
  document.addEventListener('visibilitychange', () => {
    document.hidden ? clearInterval(timer) : startTimer();
  });

  startTimer();
})();
