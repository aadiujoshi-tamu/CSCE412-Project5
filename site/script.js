const observer = new IntersectionObserver((entries) => {
  for (const entry of entries) {
    if (entry.isIntersecting) {
      entry.target.classList.add('is-visible');
      observer.unobserve(entry.target);
    }
  }
}, { threshold: 0.12 });

document.querySelectorAll('.intro-content, .architecture-heading, .flow-step, .principle, .delivery-copy, .delivery-orb, .endnote').forEach((element) => {
  element.classList.add('reveal');
  observer.observe(element);
});

document.querySelectorAll('[data-filter]').forEach((button) => {
  button.addEventListener('click', () => {
    const filter = button.dataset.filter;
    document.querySelectorAll('[data-filter]').forEach((item) => item.setAttribute('aria-pressed', String(item === button)));
    document.querySelectorAll('.service-card').forEach((card) => {
      card.classList.toggle('is-hidden', filter !== 'all' && card.dataset.category !== filter);
    });
  });
});

const form = document.querySelector('[data-contact-form]');
if (form) {
  form.addEventListener('submit', (event) => {
    event.preventDefault();
    const message = form.querySelector('.form-message');
    if (!form.checkValidity()) {
      message.textContent = 'Please complete each field with a valid email address.';
      form.reportValidity();
      return;
    }
    message.textContent = 'Thanks. This static demo validated your message locally; nothing was sent.';
    form.reset();
  });
}
