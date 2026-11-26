
(function(){
  /* Menú móvil */
  var nav = document.querySelector('.nav'), btn = document.getElementById('menuBtn');
  if (btn){ btn.addEventListener('click', function(){ var open = nav.classList.toggle('open'); btn.setAttribute('aria-expanded', open ? 'true' : 'false'); }); }
  /* Video: silencioso en bucle; con el botón arranca de cero con sonido */
  var vp = document.getElementById('videoPlanta'), vframe = document.getElementById('videoFrame'), vbtn = document.getElementById('videoSound');
  var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches, soundMode = false;
  if (vp && reduce){ vp.removeAttribute('autoplay'); vp.pause(); vp.setAttribute('controls', ''); }
  if (vbtn && vp) vbtn.addEventListener('click', function(){
    soundMode = true; vframe.classList.add('sound');
    vp.muted = false; vp.loop = false; vp.controls = true; vp.currentTime = 0; vp.play().catch(function(){});
  });
  if (vp) vp.addEventListener('ended', function(){
    if (!soundMode) return;
    soundMode = false; vframe.classList.remove('sound');
    vp.controls = false; vp.muted = true; vp.loop = true; vp.currentTime = 0;
    if (!reduce) vp.play().catch(function(){});
  });
  /* Formulario: arma el mensaje y abre WhatsApp */
  var form = document.getElementById('formContacto');
  if (form){
    form.addEventListener('submit', function(e){
      e.preventDefault();
      var g = function(id){ var el = document.getElementById(id); return el ? el.value.trim() : ''; };
      var t = form.getAttribute('data-t').split('|');
      var parts = [t[0] + ' ' + (g('fNombre') || '-') + (g('fEmpresa') ? ' ' + t[1] + ' ' + g('fEmpresa') : '') + '.'];
      if (g('fProd')) parts.push(t[2] + ' ' + g('fProd') + '.');
      if (g('fMsg')) parts.push(t[3] + ' ' + g('fMsg'));
      if (g('fTel')) parts.push('Tel: ' + g('fTel'));
      window.open('https://wa.me/5492216422421?text=' + encodeURIComponent(parts.join(' ')), '_blank', 'noopener');
    });
  }
})();
