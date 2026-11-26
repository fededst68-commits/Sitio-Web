(function(){
  var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var lang = (document.documentElement.lang || 'es').slice(0, 2) === 'en' ? 'en' : 'es';
  var JS_STR = {
    es: { fib_capas:['Celulosa regenerada','papel de fibra, resistente y permeable'], fib_corrugado:['Corrugado propio','plisada en tubos'], fib_ei:['Embutido inmediato','sin remojo, lista al plisar'], fib_calibre:['Calibre','Ø120'],
      prod:['salame recto y longaniza','salame Milán y bresaola','bondiola, panceta y lomo','jamón y mortadela'], calibre:'Calibre', plisando:'plisando',
      tipo:'Tipo de red', elastica:'elástica', sinel:'sin elastizar, rombo o hexágono', compresion:'Compresión', doble:'doble elástico: dos hilos en la trama', estandar:'estándar', amedida:'a medida',
      hilado:'Hilado y color', colores:['blanco','rojo','natural'], hilado_sfx:' · poliéster, algodón o compostable', cuadros:'Cuadros', cuadros_l:'cuadros', rollos:['rollo 50 m','rollo 50 m','rollo 50 m','rollo 100 m'],
      kosher:'Rito kosher', kosher_v:'huachalomo y roast beef · ±24 a ±44 cm',
      title:'Prototipo De Stefano Insumos', desc:'Prototipo de rediseño del sitio de De Stefano Insumos: tripas fibrosas Fibrø® y redes Enets® presentadas con scroll.', wa:'Hola, quiero consultar por insumos De Stefano' },
    en: { fib_capas:['Regenerated cellulose','fibre paper, strong and permeable'], fib_corrugado:['In-house shirring','shirred into sticks'], fib_ei:['Ready to use','no soaking, ready once shirred'], fib_calibre:['Calibre','Ø120'],
      prod:['straight salami and longaniza','Milano salami and bresaola','coppa, pork belly and loin','ham and mortadella'], calibre:'Calibre', plisando:'shirring',
      tipo:'Net type', elastica:'elastic', sinel:'non-elastic, diamond or hexagonal', compresion:'Compression', doble:'double elastic: two threads in the weft', estandar:'standard', amedida:'custom',
      hilado:'Yarn and colour', colores:['white','red','natural'], hilado_sfx:' · polyester, cotton or compostable', cuadros:'Squares', cuadros_l:'squares', rollos:['50 m roll','50 m roll','50 m roll','100 m roll'],
      kosher:'Kosher', kosher_v:'huachalomo and roast beef · ±24 to ±44 cm',
      title:'De Stefano Insumos prototype', desc:'Redesign prototype for the De Stefano Insumos website: Fibrø® fibrous casings and Enets® nets presented with scroll.', wa:'Hello, I would like to ask about De Stefano supplies' }
  };
  function S(k){ return JS_STR[lang][k]; }
  var mobile = window.matchMedia ? window.matchMedia('(max-width: 820px)') : { matches: false };
  var ease = reduce ? 1 : 0.14;
  function clamp(v,a,b){ return Math.min(b, Math.max(a, v)); }
  /* Línea de activación: en escritorio, al 58 % del alto de la ventana; en celular, justo debajo del visual fijo. */
  function lineFor(s){
    if (mobile.matches){ return s.box.getBoundingClientRect().bottom + 16; }
    return window.innerHeight * 0.58;
  }
  function progressOf(el, line){
    var r = el.getBoundingClientRect();
    return clamp((line - r.top) / r.height, 0, 1);
  }
  function inView(el){
    var r = el.getBoundingClientRect();
    return r.bottom > -200 && r.top < window.innerHeight + 200;
  }
  function setAttrs(el, o){ for (var k in o) el.setAttribute(k, o[k]); }

  /* Activación de pasos por scroll: queda activo el último paso cuyo borde superior pasó la línea. */
  var stories = {};
  Array.prototype.forEach.call(document.querySelectorAll('[data-story]'), function(st){
    var steps = Array.prototype.slice.call(st.querySelectorAll('.step'));
    var svg = st.querySelector('svg');
    var s = { el: st, steps: steps, svg: svg, box: st.querySelector('.visual-box'), active: null };
    s.activate = function(step){
      if (s.active === step) return;
      s.active = step;
      steps.forEach(function(x){ x.classList.toggle('is-active', x === step); });
      svg.setAttribute('data-state', step.getAttribute('data-state'));
    };
    s.update = function(){
      var line = lineFor(s), pick = steps[0];
      for (var i = 0; i < steps.length; i++){
        if (steps[i].getBoundingClientRect().top <= line) pick = steps[i];
      }
      s.activate(pick);
      return line;
    };
    stories[st.getAttribute('data-story')] = s;
    s.activate(steps[0]);
  });

  /* Fibrø: diámetro y lecturas */
  var fib = stories.fibro, fibD = 150, fibTarget = 150, pleat = 0, pleatT = 0;
  var fibEls = {
    body: document.getElementById('bodyRect'),
    fibra: document.getElementById('bodyFibra'),
    pliegue: document.getElementById('bodyPliegue'),
    borde: document.getElementById('bodyBorde'),
    plD: document.getElementById('plD'),
    plL: document.getElementById('plL'),
    pat: document.getElementById('pPliegue'),
    end: document.getElementById('gEnd'),
    clip: document.getElementById('clipRect'),
    capL: document.getElementById('capL'),
    lineL: document.getElementById('calLineL'),
    tickT: document.getElementById('calTickT'),
    tickB: document.getElementById('calTickB'),
    calText: document.getElementById('calText'),
    label: document.getElementById('fibroLabel'),
    value: document.getElementById('fibroValue')
  };
  function fibReadout(k){ return S('fib_' + k); }
  function productoPara(mm){ var p = S('prod'); return mm < 80 ? p[0] : mm < 107 ? p[1] : mm < 165 ? p[2] : p[3]; }
  /* D = diámetro; q = grado de plisado (0 = tripa lisa de 420 px, 1 = tubo plisado de 270 px).
     Al plisar, el largo se acorta, los extremos se aplanan, los pliegues aparecen cada vez más juntos
     y al final se ve la cara hueca del tubo. */
  function applyD(D, q){
    var y = 210 - D/2, L = 420 - 150 * q, x = 320 + 15 * q - L / 2, r = (D/2) * (1 - q) + 10 * q;
    [fibEls.body, fibEls.fibra, fibEls.pliegue, fibEls.borde, fibEls.clip].forEach(function(el){ setAttrs(el, {x:x, y:y, width:L, height:D, rx:r}); });
    fibEls.fibra.setAttribute('opacity', 1 - q);
    fibEls.pliegue.setAttribute('opacity', Math.min(1, q * 1.4));
    fibEls.borde.setAttribute('opacity', q);
    var period = 5 + 11 * (1 - q) * (1 - q);
    setAttrs(fibEls.pat, {width: period});
    setAttrs(fibEls.plD, {width: period * 0.24});
    setAttrs(fibEls.plL, {x: period * 0.48, width: period * 0.2});
    setAttrs(fibEls.capL, {cx: x + 10, ry: D/2});
    fibEls.capL.setAttribute('opacity', 1 - q);
    var k = D / 150, eo = Math.max(0, (q - 0.6) / 0.4);
    fibEls.end.setAttribute('transform', 'translate(' + x + ' 210) scale(' + k + ')');
    fibEls.end.setAttribute('opacity', eo);
    setAttrs(fibEls.lineL, {y1:y, y2:y+D});
    setAttrs(fibEls.tickT, {y1:y, y2:y});
    setAttrs(fibEls.tickB, {y1:y+D, y2:y+D});
  }

  /* Enets: pieza, red y lecturas */
  var en = stories.enets;
  var enEls = {
    body: document.getElementById('piezaBody'),
    clip: document.getElementById('piezaClip'),
    sheen: document.getElementById('piezaSheen'),
    rings: document.getElementById('ringsPath'),
    longG: document.getElementById('longLines'),
    hex: document.getElementById('hexPath'),
    netCuadro: document.getElementById('netCuadro'),
    netHex: document.getElementById('netHex'),
    label: document.getElementById('enetsLabel'),
    value: document.getElementById('enetsValue')
  };
  /* La pieza es un ovoide (elipsoide de revolución) visto un poco desde su extremo derecho: el radio
     varía a lo largo del eje, los hilos transversales son arcos que se achican hacia las puntas y los
     longitudinales son meridianos que convergen en los extremos. Al hacer scroll, la malla corre a lo
     largo de la pieza, como una lámina detrás de una ventana ovalada. */
  var pz = { w:308, h:200, cells:20, doble:0 }, pzT = { w:308, h:200, cells:20 };
  var colores = ['#F6F1E8', '#A8321E', '#D9C8A3'];
  var CY = 210, SVG_NS = 'http://www.w3.org/2000/svg';
  var longLines = [];
  for (var li = 0; li < 40; li++){
    var p = document.createElementNS(SVG_NS, 'path');
    p.setAttribute('stroke', 'currentColor'); p.setAttribute('fill', 'none'); p.setAttribute('stroke-linecap', 'round');
    enEls.longG.appendChild(p); longLines.push(p);
  }
  function f1(n){ return Math.round(n * 10) / 10; }
  function applyPieza(scrollOff){
    var R = pz.h / 2, A = pz.w / 2, CX = 320, x0 = CX - A, x1 = CX + A, tilt = 0.16;
    [enEls.body, enEls.clip, enEls.sheen].forEach(function(el){ setAttrs(el, {cx: CX, cy: CY, rx: f1(A), ry: f1(R)}); });
    /* radio del ovoide en la posición axial u */
    function rad(u){ var t = (u - CX) / A; var q = 1 - t * t; return q <= 0 ? 0 : R * Math.sqrt(q); }
    /* proyección: el frente del anillo se curva hacia la izquierda según la inclinación */
    function P(uu, ph){ var r = rad(uu); return f1(uu - tilt * r * Math.cos(ph)) + ' ' + f1(CY + r * Math.sin(ph)); }
    /* paso de la malla: celdas cuadradas en la parte más ancha */
    var cells = Math.max(8, pz.cells), s = Math.min(64, Math.max(9, (2 * Math.PI * R) / cells));
    var off = ((scrollOff * 0.45) % s + s) % s;
    /* anillos transversales (arcos del frente); doble elástico = dos hilos juntos */
    var d = '', dd = Math.max(2.4, s * 0.14);
    for (var u = x0 - s + off; u < x1 + s; u += s){
      var us = pz.doble > 0.02 ? [u - dd * pz.doble, u + dd * pz.doble] : [u];
      for (var k = 0; k < us.length; k++){
        var r = rad(us[k]); if (r < 2) continue;
        d += 'M' + f1(us[k]) + ' ' + f1(CY - r) + ' A' + f1(tilt * r) + ' ' + f1(r) + ' 0 0 0 ' + f1(us[k]) + ' ' + f1(CY + r) + ' ';
      }
    }
    enEls.rings.setAttribute('d', d);
    var wBase = Math.min(3, Math.max(1.1, s * 0.11));
    enEls.rings.setAttribute('stroke-width', f1(wBase * (1 - 0.2 * pz.doble)));
    enEls.hex.setAttribute('stroke-width', f1(Math.min(2.4, Math.max(1, s * 0.09))));
    /* meridianos: mitad visible del ovoide, ángulos parejos => se juntan hacia arriba, abajo y las puntas */
    var n = Math.max(4, Math.round(cells / 2)), steps = 28;
    for (var j = 0; j < longLines.length; j++){
      if (j > n){ longLines[j].setAttribute('d', ''); continue; }
      var phi = -Math.PI / 2 + j * Math.PI / n, c = Math.cos(phi), md = '';
      for (var i2 = 0; i2 <= steps; i2++){
        var uu2 = x0 + (x1 - x0) * i2 / steps;
        md += (i2 ? 'L' : 'M') + P(uu2, phi) + ' ';
      }
      longLines[j].setAttribute('d', md);
      longLines[j].setAttribute('stroke-width', f1(wBase * (0.4 + 0.65 * c)));
      longLines[j].setAttribute('stroke-opacity', f1(0.5 + 0.5 * c));
    }
    /* malla hexagonal (sin elastizar): zigzags a lo largo y conectores, proyectados sobre el ovoide */
    var hs = s * 1.15, rows = Math.max(3, Math.round(cells / 2)), hd = '';
    var dphi = Math.PI / rows, a = dphi * 0.28;
    for (var r = 0; r <= rows; r++){
      var ph0 = -Math.PI / 2 + r * dphi, sgn = (r % 2 ? -1 : 1), first = true;
      for (var uu = x0 - hs + off; uu <= x1 + hs; uu += hs / 2){
        var ph = ph0 + sgn * a; sgn = -sgn;
        hd += (first ? 'M' : 'L') + P(uu, ph) + ' '; first = false;
      }
    }
    for (var r2 = 0; r2 < rows; r2++){
      var phA = -Math.PI / 2 + r2 * dphi, phB = phA + dphi, s2 = (r2 % 2 ? -1 : 1);
      for (var u2 = x0 - hs + off + (r2 % 2 ? hs / 2 : 0); u2 <= x1 + hs; u2 += hs){
        hd += 'M' + P(u2, phA + a) + ' L' + P(u2, phB - a) + ' ';
      }
    }
    enEls.hex.setAttribute('d', hd);
  }

  function tick(){
    /* Fibrø */
    if (fib && inView(fib.el)){
      var fline = fib.update();
      var fs = fib.active.getAttribute('data-state');
      var ro = fibReadout(fs);
      if (fs === 'calibre'){
        var p = progressOf(fib.active, fline);
        var mm = Math.round(45 + p * 150);
        fibTarget = mm * 1.3; pleatT = 0;
        fibEls.calText.textContent = 'Ø' + mm;
        fibEls.label.textContent = S('calibre') + ' Ø' + mm;
        fibEls.value.textContent = productoPara(mm);
      } else if (fs === 'corrugado'){
        /* el plisado avanza con el scroll dentro de este paso */
        var pq = Math.min(1, progressOf(fib.active, fline) * 1.6);
        fibTarget = 150; pleatT = pq;
        fibEls.label.textContent = ro[0];
        fibEls.value.textContent = pq < 0.98 ? S('plisando') + ' ' + Math.round(pq * 100) + ' %' : ro[1];
      } else {
        fibTarget = 150; pleatT = fs === 'ei' ? 1 : 0;
        fibEls.label.textContent = ro[0];
        fibEls.value.textContent = ro[1];
      }
      fibD += (fibTarget - fibD) * ease;
      pleat += (pleatT - pleat) * (reduce ? 1 : 0.18);
      applyD(fibD, pleat);
    }
    /* Enets */
    if (en && inView(en.el)){
      var eline = en.update();
      var es = en.active.getAttribute('data-state');
      var q = progressOf(en.active, eline);
      var hex = 0, doble = 0;
      pzT.w = 308; pzT.h = 200; pzT.cells = 20;
      var color = colores[0];
      if (es === 'tipo'){
        hex = q >= 0.5 ? 1 : 0;
        enEls.label.textContent = S('tipo');
        enEls.value.textContent = hex ? S('sinel') : S('elastica');
      } else if (es === 'compresion'){
        var k = q;
        doble = k >= 0.5 ? 1 : 0;
        pzT.w = 308 + 50 * k; pzT.h = 200 - 46 * k;
        enEls.label.textContent = S('compresion');
        enEls.value.textContent = doble ? S('doble') : (k < 0.25 ? S('estandar') : S('amedida'));
      } else if (es === 'hilado'){
        var i = Math.min(2, Math.floor(q * 3));
        color = colores[i];
        enEls.label.textContent = S('hilado');
        enEls.value.textContent = S('colores')[i] + S('hilado_sfx');
      } else if (es === 'cuadros'){
        var cu = [14, 20, 44, 60], rollos = S('rollos');
        var j = Math.min(3, Math.floor(q * 4));
        pzT.cells = cu[j];
        enEls.label.textContent = S('cuadros');
        enEls.value.textContent = cu[j] + ' ' + S('cuadros_l') + ' · ' + rollos[j];
      } else if (es === 'kosher'){
        pzT.cells = 12;
        enEls.label.textContent = S('kosher');
        enEls.value.textContent = S('kosher_v');
      }
      enEls.netHex.style.opacity = hex;
      enEls.netCuadro.style.opacity = 1 - hex;
      en.svg.style.color = color;
      pz.w += (pzT.w - pz.w) * ease;
      pz.h += (pzT.h - pz.h) * ease;
      pz.cells += (pzT.cells - pz.cells) * ease;
      pz.doble += (doble - pz.doble) * ease;
      applyPieza(window.scrollY || window.pageYOffset || 0);
    }
    window.requestAnimationFrame(tick);
  }
  applyD(fibD, 0); applyPieza(0);
  window.requestAnimationFrame(tick);

})();
