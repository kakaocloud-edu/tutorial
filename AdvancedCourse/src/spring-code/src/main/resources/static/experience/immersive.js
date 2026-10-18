(() => {
    'use strict';
    const story = document.getElementById('lab-story');
    const lab = document.getElementById('lab');
    const original = story?.querySelector('.lab-original');
    const content = original?.querySelector('.content');
    const overlay = document.getElementById('cloud-experience');
    const canvas = document.getElementById('immersive-canvas');
    if (!story || !lab || !original || !content || !overlay || !canvas) return;

    const scene = overlay.querySelector('.immersive-scene');
    const poster = overlay.querySelector('.immersive-poster');
    const benefits = Array.from(overlay.querySelectorAll('[data-benefit]'));
    const returnLink = overlay.querySelector('.immersive-return');
    const sourceLink = overlay.querySelector('.immersive-source');
    const reduced = window.matchMedia('(prefers-reduced-motion: reduce)');
    const mobile = window.matchMedia('(max-width: 680px)');
    const short = window.matchMedia('(max-height: 640px)');
    const frameCount = Math.max(1, Number(overlay.dataset.frameCount) || 1);
    const framePattern = overlay.dataset.framePattern;
    const frameWidth = Number(overlay.dataset.frameWidth) || 1280;
    const frameHeight = Number(overlay.dataset.frameHeight) || 720;
    const context = canvas.getContext('2d', { alpha: false });
    const frames = new Map();
    const pending = new Map();
    const failed = new Set();
    const intervals = [[.22, .31, .40, .45], [.445, .51, .60, .66], [.675, .76, .88, .98]];
    const circles = [
        { element: original.querySelector('.shape-flight-blue .animated-circle'), scale: 1 },
        { element: original.querySelector('.shape-flight-yellow .animated-circle'), scale: 1 }
    ];
    let motion = false;
    let baseHeight = window.innerHeight;
    let needsMeasure = true;
    let ticking = false;
    let visible = false;
    let targetFrame = 0;
    let renderedFrame = -1;
    let direction = 1;
    let pulseFrozen = false;
    let posterFallback = false;
    let formatUnavailable = false;

    const clamp = (value, lower = 0, upper = 1) => Math.max(lower, Math.min(upper, value));
    const smooth = (start, end, value) => {
        const unit = clamp((value - start) / (end - start));
        return unit * unit * (3 - 2 * unit);
    };
    const value = (name, amount, unit = '') => story.style.setProperty(name, `${amount}${unit}`);
    const schedule = () => {
        if (ticking) return;
        ticking = true;
        window.requestAnimationFrame(update);
    };

    function accessibility(element, hidden) {
        element.setAttribute('aria-hidden', String(hidden));
        element.inert = hidden;
    }

    function measure() {
        const padding = window.getComputedStyle(original);
        baseHeight = Math.max(window.innerHeight,
            content.offsetHeight + parseFloat(padding.paddingTop) + parseFloat(padding.paddingBottom));
        const extra = Math.max(0, baseHeight - window.innerHeight);
        value('--lab-base-height', baseHeight, 'px');
        value('--lab-sticky-top', -extra, 'px');
        value('--immersive-top', extra, 'px');
        needsMeasure = false;
    }

    function loadPoster(staticMode = false) {
        const source = (staticMode || posterFallback) && poster.dataset.staticSrc
            ? poster.dataset.staticSrc : poster.dataset.src;
        if (source && poster.getAttribute('src') !== source) poster.src = source;
    }

    function fit() {
        const width = canvas.clientWidth || overlay.clientWidth || original.clientWidth;
        const height = canvas.clientHeight || window.innerHeight;
        const scale = Math.min(width / frameWidth, height / frameHeight);
        const x = (width - frameWidth * scale) / 2;
        const y = (height - frameHeight * scale) / 2;
        value('--film-fit-scale', scale);
        value('--film-fit-x', x, 'px');
        value('--film-fit-y', y, 'px');
        return { width, height, scale, x, y };
    }

    function freezePulse(frozen, travel = 0) {
        if (frozen && !pulseFrozen) {
            circles.forEach(circle => {
                if (!circle.element) return;
                const transform = window.getComputedStyle(circle.element).transform;
                const matrix = transform === 'none' ? [] : transform.match(/matrix\(([^)]+)\)/)?.[1].split(',').map(Number);
                circle.scale = matrix?.length ? Math.hypot(matrix[0], matrix[1]) : 1;
                circle.element.style.animation = 'none';
            });
        }
        circles.forEach(circle => {
            if (!circle.element) return;
            if (frozen) circle.element.style.transform = `scale(${circle.scale + (1 - circle.scale) * travel})`;
            else {
                circle.element.style.removeProperty('animation');
                circle.element.style.removeProperty('transform');
            }
        });
        pulseFrozen = frozen;
    }

    function paint() {
        if (!context || !frames.size) return;
        const bounds = fit();
        const density = Math.min(window.devicePixelRatio || 1, 1.5);
        const width = Math.round(bounds.width * density);
        const height = Math.round(bounds.height * density);
        if (!width || !height) return;
        if (canvas.width !== width || canvas.height !== height) {
            canvas.width = width;
            canvas.height = height;
            renderedFrame = -1;
        }
        const nearest = frames.has(targetFrame) ? targetFrame : Array.from(frames.keys()).reduce((best, index) =>
            Math.abs(index - targetFrame) < Math.abs(best - targetFrame) ? index : best);
        if (renderedFrame === nearest) return;
        const image = frames.get(nearest);
        const scale = Math.min(width / image.naturalWidth, height / image.naturalHeight);
        const imageWidth = image.naturalWidth * scale;
        const imageHeight = image.naturalHeight * scale;
        context.fillStyle = '#1a1a2e';
        context.fillRect(0, 0, width, height);
        context.drawImage(image, (width - imageWidth) / 2, (height - imageHeight) / 2, imageWidth, imageHeight);
        renderedFrame = nearest;
        canvas.dataset.frame = String(nearest);
        scene.classList.add('is-ready');
    }

    function cancelPending(distantOnly = false) {
        pending.forEach((image, index) => {
            if (distantOnly && Math.abs(index - targetFrame) <= 12) return;
            pending.delete(index);
            image.onload = null;
            image.onerror = null;
            image.removeAttribute('src');
        });
    }

    function trimFrames() {
        const farthest = Array.from(frames.keys()).sort((a, b) =>
            Math.abs(b - targetFrame) - Math.abs(a - targetFrame));
        while (frames.size > 14) frames.delete(farthest.shift());
    }

    function preload() {
        if (!motion || !visible || document.hidden) return;
        cancelPending(true);
        const candidates = [targetFrame];
        for (let distance = 1; distance <= 6; distance++) {
            candidates.push(targetFrame + distance * direction, targetFrame - distance * direction);
        }
        for (const index of candidates) {
            if (pending.size >= 4) break;
            if (index < 0 || index >= frameCount || frames.has(index) || pending.has(index) || failed.has(index)) continue;
            const image = new Image();
            pending.set(index, image);
            image.decoding = 'async';
            image.onload = () => {
                if (pending.get(index) !== image) return;
                pending.delete(index);
                if (motion && visible && !document.hidden && Math.abs(index - targetFrame) <= 12) {
                    frames.set(index, image);
                    trimFrames();
                }
                schedule();
            };
            image.onerror = () => {
                if (pending.get(index) !== image) return;
                pending.delete(index);
                failed.add(index);
                if (!frames.size && failed.has(0)) {
                    useStaticFallback();
                }
                schedule();
            };
            image.src = framePattern.replace('{index}', String(index).padStart(3, '0'));
        }
    }

    function pose(progress) {
        const travel = smooth(.02, .12, progress);
        const retreat = smooth(.025, .16, progress);
        const image = fit();
        const extra = Math.max(0, baseHeight - window.innerHeight);
        const blueTargetScale = 120 * image.scale / 100;
        const yellowTargetScale = 139.5 * image.scale / 100;
        const ready = renderedFrame >= 0 || (poster.complete && poster.naturalWidth > 0);
        const reveal = ready ? smooth(.12, .18, progress) : 0;
        const height = window.innerHeight;
        freezePulse(motion && progress > .02, travel);
        value('--lab-progress', progress.toFixed(5));
        value('--lab-content-opacity', 1 - retreat);
        value('--lab-content-y', -height * .10 * smooth(.025, .24, progress), 'px');
        value('--lab-content-scale', 1 - .04 * retreat);
        value('--blue-x', travel * (image.x + 978.5 * image.scale - 100 * blueTargetScale), 'px');
        value('--blue-y', travel * (extra + image.y + 226.5 * image.scale - 50 * blueTargetScale), 'px');
        value('--blue-scale', 1 + (blueTargetScale - 1) * travel);
        value('--blue-opacity', 1 - reveal);
        value('--blue-blur', 0, 'px');
        value('--yellow-x', travel * (image.x + 839 * image.scale - 20 * yellowTargetScale), 'px');
        value('--yellow-y', travel * (extra + image.y + 426 * image.scale - 100 * yellowTargetScale), 'px');
        value('--yellow-scale', 1 + (yellowTargetScale - 1) * travel);
        value('--yellow-opacity', 1 - reveal);
        value('--yellow-blur', 0, 'px');
        value('--lab-veil', .65 * reveal);
        value('--lab-scene-opacity', reveal);
        value('--lab-return-opacity', smooth(.14, .22, progress));
        value('--lab-source-opacity', smooth(.76, .86, progress));
        accessibility(content, retreat > .98);
        accessibility(overlay, progress < .12);
        accessibility(returnLink, progress < .16);
        accessibility(sourceLink, progress < .80);

        benefits.forEach((benefit, index) => {
            const [start, arrive, depart, end] = intervals[index];
            const enter = smooth(start, arrive, progress);
            const exit = smooth(depart, end, progress);
            const opacity = enter * (1 - exit);
            benefit.style.setProperty('--benefit-opacity', opacity.toFixed(5));
            benefit.style.setProperty('--benefit-y', `${46 * (1 - enter) - 38 * exit}px`);
            benefit.style.setProperty('--benefit-scale', String(.98 + .02 * enter - .015 * exit));
            accessibility(benefit, opacity < .03);
            benefit.style.visibility = opacity < .001 ? 'hidden' : 'visible';
        });
    }

    function update() {
        ticking = false;
        if (needsMeasure) measure();
        if (!motion) {
            const bounds = overlay.getBoundingClientRect();
            if (bounds.top < window.innerHeight && bounds.bottom > 0) loadPoster(true);
            return;
        }
        const bounds = story.getBoundingClientRect();
        const range = Math.max(1, story.offsetHeight - baseHeight);
        const extra = Math.max(0, baseHeight - window.innerHeight);
        const progress = clamp((-bounds.top - extra) / range);
        const next = Math.round(clamp((progress - .18) / .76) * (frameCount - 1));
        if (next !== targetFrame) direction = next > targetFrame ? 1 : -1;
        targetFrame = next;
        visible = progress > .018 && bounds.bottom > 0 && bounds.top < window.innerHeight;
        if (visible && !document.hidden) {
            loadPoster();
            paint();
            preload();
        } else cancelPending();
        pose(progress);
    }

    function preferencesChanged() {
        motion = Boolean(context) && !formatUnavailable && !reduced.matches && !mobile.matches && !short.matches;
        document.body.dataset.immersive = motion ? 'on' : 'off';
        needsMeasure = true;
        if (!motion) {
            pose(0);
            accessibility(content, false);
            accessibility(overlay, false);
            accessibility(returnLink, false);
            accessibility(sourceLink, false);
            benefits.forEach(benefit => { accessibility(benefit, false); benefit.style.visibility = 'visible'; });
            frames.clear();
            cancelPending();
            scene.classList.remove('is-ready');
            renderedFrame = -1;
        }
        schedule();
    }

    function useStaticFallback() {
        posterFallback = true;
        if (overlay.dataset.frameFormat === 'avif' && renderedFrame < 0) {
            formatUnavailable = true;
            preferencesChanged();
        }
        if (!document.hidden) loadPoster(!motion);
        schedule();
    }

    poster.addEventListener('load', schedule);
    poster.addEventListener('error', () => {
        if (posterFallback || !motion) return;
        useStaticFallback();
    });

    returnLink.addEventListener('click', event => {
        if (event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
        event.preventDefault();
        window.scrollTo({ top: story.getBoundingClientRect().top + window.scrollY, behavior: 'auto' });
        if (event.detail === 0) {
            original.setAttribute('tabindex', '-1');
            original.focus({ preventScroll: true });
        }
    });
    window.addEventListener('scroll', schedule, { passive: true });
    window.addEventListener('resize', () => { needsMeasure = true; schedule(); }, { passive: true });
    document.addEventListener('visibilitychange', schedule);
    reduced.addEventListener('change', preferencesChanged);
    mobile.addEventListener('change', preferencesChanged);
    short.addEventListener('change', preferencesChanged);
    if ('ResizeObserver' in window) new ResizeObserver(() => { needsMeasure = true; schedule(); }).observe(content);
    preferencesChanged();
})();
