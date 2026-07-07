const form = document.getElementById('searchForm');
const submitBtn = document.getElementById('submitBtn');
const loading = document.getElementById('loading');
const errorBox = document.getElementById('errorBox');
const emptyState = document.getElementById('emptyState');
const resultsContainer = document.getElementById('results');

const submitBtnDefault = submitBtn.innerHTML;

const sentimentTitles = {
    positive: 'Comentários Positivos',
    neutral: 'Comentários Neutros',
    negative: 'Comentários Negativos'
};

function escapeHtml(value) {
    return String(value ?? '')
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
}

function formatNumber(value) {
    const n = Number(value) || 0;
    return n.toLocaleString('pt-BR');
}

function setLoading(isLoading) {
    if (isLoading) {
        loading.classList.add('active');
        submitBtn.disabled = true;
        submitBtn.innerHTML = `
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none"
                 stroke="currentColor" stroke-width="2.5"
                 stroke-linecap="round" stroke-linejoin="round"
                 style="animation: spin 0.8s linear infinite;">
                <path d="M21 12a9 9 0 1 1-6.219-8.56"></path>
            </svg>
            Analisando...
        `;
    } else {
        loading.classList.remove('active');
        submitBtn.disabled = false;
        submitBtn.innerHTML = submitBtnDefault;
    }
}

function showError(message) {
    errorBox.textContent = message;
    errorBox.style.display = 'block';
}

function clearError() {
    errorBox.textContent = '';
    errorBox.style.display = 'none';
}

function renderCharts(graficoEngajamento, graficoSentimentos) {
    if (!graficoEngajamento || !graficoSentimentos) return '';

    return `
        <div class="charts-grid">
            <div class="chart-card">
                <div class="chart-card-header">
                    <div>
                        <div class="chart-title">Engajamento por Vídeo</div>
                        <div class="chart-subtitle">
                            Comparativo de likes e views — barras de likes
                            coloridas pelo sentimento predominante.
                        </div>
                    </div>
                    <div class="chart-icon">
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none"
                             stroke="currentColor" stroke-width="2"
                             stroke-linecap="round" stroke-linejoin="round">
                            <path d="M3 3v18h18"></path>
                            <rect x="7" y="13" width="3" height="5"></rect>
                            <rect x="12" y="9" width="3" height="9"></rect>
                            <rect x="17" y="5" width="3" height="13"></rect>
                        </svg>
                    </div>
                </div>
                <div class="chart-image" data-zoomable>
                    <img src="data:image/png;base64,${graficoEngajamento}"
                         alt="Gráfico de Engajamento por Vídeo">
                    <div class="chart-zoom-hint">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none"
                             stroke="currentColor" stroke-width="2.5"
                             stroke-linecap="round" stroke-linejoin="round">
                            <circle cx="11" cy="11" r="7"></circle>
                            <path d="m21 21-4.3-4.3"></path>
                            <path d="M11 8v6"></path>
                            <path d="M8 11h6"></path>
                        </svg>
                    </div>
                </div>
            </div>

            <div class="chart-card">
                <div class="chart-card-header">
                    <div>
                        <div class="chart-title">Distribuição de Sentimentos</div>
                        <div class="chart-subtitle">
                            Quantidade de comentários classificados como
                            positivos, neutros e negativos por vídeo.
                        </div>
                    </div>
                    <div class="chart-icon">
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none"
                             stroke="currentColor" stroke-width="2"
                             stroke-linecap="round" stroke-linejoin="round">
                            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
                        </svg>
                    </div>
                </div>
                <div class="chart-image" data-zoomable>
                    <img src="data:image/png;base64,${graficoSentimentos}"
                         alt="Gráfico de Distribuição de Sentimentos">
                    <div class="chart-zoom-hint">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none"
                             stroke="currentColor" stroke-width="2.5"
                             stroke-linecap="round" stroke-linejoin="round">
                            <circle cx="11" cy="11" r="7"></circle>
                            <path d="m21 21-4.3-4.3"></path>
                            <path d="M11 8v6"></path>
                            <path d="M8 11h6"></path>
                        </svg>
                    </div>
                </div>
            </div>
        </div>
    `;
}

function renderComments(comentarios) {
    return (comentarios || []).map(c => `
        <div class="comment ${escapeHtml(c.sentimento)}"
             data-sentiment="${escapeHtml(c.sentimento)}" hidden>
            ${c.autor ? `<div class="comment-author">${escapeHtml(c.autor)}</div>` : ''}
            <div class="comment-text">${escapeHtml(c.texto)}</div>
        </div>
    `).join('');
}

function renderSentimentBadge(pos, neu, neg) {
    if (pos >= neg && pos >= neu) {
        return '<span class="sentiment-badge badge-positive">Positivo</span>';
    }
    if (neg >= pos && neg >= neu) {
        return '<span class="sentiment-badge badge-negative">Negativo</span>';
    }
    return '<span class="sentiment-badge badge-neutral">Neutro</span>';
}

function renderVideoCard(video) {
    const s = video.sentimentos || { positive: 0, neutral: 0, negative: 0 };
    const pos = s.positive || 0;
    const neu = s.neutral || 0;
    const neg = s.negative || 0;
    const total = pos + neu + neg;
    const est = video.estatisticas || {};

    let sentimentBody;

    if (total > 0) {
        const pPos = (pos / total * 100).toFixed(1);
        const pNeu = (neu / total * 100).toFixed(1);
        const pNeg = (neg / total * 100).toFixed(1);

        sentimentBody = `
            <div class="sentiment-bar">
                <div class="bar-positive" style="width: ${pPos}%"></div>
                <div class="bar-neutral" style="width: ${pNeu}%"></div>
                <div class="bar-negative" style="width: ${pNeg}%"></div>
            </div>

            <div class="sentiment-legend">
                <button type="button" class="legend-item legend-positive"
                        data-sentiment="positive" ${pos === 0 ? 'disabled' : ''}
                        title="Ver comentários positivos">
                    <span class="legend-dot dot-positive"></span>
                    Positivos: <strong>${pos}</strong>
                </button>
                <button type="button" class="legend-item legend-neutral"
                        data-sentiment="neutral" ${neu === 0 ? 'disabled' : ''}
                        title="Ver comentários neutros">
                    <span class="legend-dot dot-neutral"></span>
                    Neutros: <strong>${neu}</strong>
                </button>
                <button type="button" class="legend-item legend-negative"
                        data-sentiment="negative" ${neg === 0 ? 'disabled' : ''}
                        title="Ver comentários negativos">
                    <span class="legend-dot dot-negative"></span>
                    Negativos: <strong>${neg}</strong>
                </button>
            </div>

            <div class="comments-panel">
                <div class="comments-title"></div>
                <div class="comments-list">
                    ${renderComments(video.comentarios)}
                    <div class="comments-empty" hidden>
                        Nenhum comentário deste tipo encontrado.
                    </div>
                </div>
            </div>
        `;
    } else {
        sentimentBody = `
            <p style="font-size: 13px; color: var(--text-muted);
                      text-align: center; padding: 8px 0;">
                Sem comentários disponíveis para análise.
            </p>
        `;
    }

    return `
        <article class="video-card">
            <div class="thumb">
                <img src="https://img.youtube.com/vi/${escapeHtml(video.videoId)}/hqdefault.jpg"
                     alt="${escapeHtml(video.titulo)}" loading="lazy">
                <div class="thumb-overlay">
                    <a href="${escapeHtml(video.url)}" target="_blank" rel="noopener"
                       class="play-link">
                        <svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor">
                            <path d="M8 5v14l11-7z"/>
                        </svg>
                        Assistir
                    </a>
                </div>
            </div>

            <div class="card-body">
                <h3 class="video-title">${escapeHtml(video.titulo)}</h3>

                <div class="stats">
                    <div class="stat">
                        <div class="stat-value">${formatNumber(est.viewCount)}</div>
                        <div class="stat-label">Views</div>
                    </div>
                    <div class="stat">
                        <div class="stat-value">${formatNumber(est.likeCount)}</div>
                        <div class="stat-label">Likes</div>
                    </div>
                    <div class="stat">
                        <div class="stat-value">${formatNumber(est.commentCount)}</div>
                        <div class="stat-label">Comentários</div>
                    </div>
                </div>

                <div class="sentiment-section">
                    <div class="sentiment-header">
                        <span class="sentiment-label">Sentimento Predominante</span>
                        ${renderSentimentBadge(pos, neu, neg)}
                    </div>
                    ${sentimentBody}
                </div>
            </div>
        </article>
    `;
}

function renderResults(data) {
    const videos = data.videos || [];

    const chartsHtml = renderCharts(
        data.grafico_engajamento,
        data.grafico_sentimentos
    );

    const cardsHtml = videos.map(renderVideoCard).join('');

    resultsContainer.innerHTML = `
        <div class="results-header">
            <h2>Resultados da Análise</h2>
            <span class="results-count">${videos.length} vídeo(s) analisado(s)</span>
        </div>
        ${chartsHtml}
        <div class="videos">${cardsHtml}</div>
    `;

    bindCommentToggles();
    bindZoomables();
}

function bindCommentToggles() {
    document.querySelectorAll('.video-card').forEach(card => {
        const buttons = card.querySelectorAll('.legend-item');
        const panel = card.querySelector('.comments-panel');
        if (!panel) return;

        const titleEl = panel.querySelector('.comments-title');
        const emptyEl = panel.querySelector('.comments-empty');
        const comments = panel.querySelectorAll('.comment');

        buttons.forEach(btn => {
            btn.addEventListener('click', () => {
                const sentiment = btn.dataset.sentiment;
                const isActive = btn.classList.contains('active');

                buttons.forEach(b => b.classList.remove('active'));

                if (isActive) {
                    panel.classList.remove('active');
                    return;
                }

                btn.classList.add('active');
                titleEl.textContent = sentimentTitles[sentiment] || '';

                let visibleCount = 0;
                comments.forEach(c => {
                    const match = c.dataset.sentiment === sentiment;
                    c.hidden = !match;
                    if (match) visibleCount++;
                });

                if (emptyEl) emptyEl.hidden = visibleCount > 0;

                panel.classList.add('active');
            });
        });
    });
}

// ===== LIGHTBOX =====
const lightbox = document.getElementById('lightbox');
const lightboxImg = document.getElementById('lightboxImg');
const lightboxClose = document.getElementById('lightboxClose');

function openLightbox(src, alt) {
    lightboxImg.src = src;
    lightboxImg.alt = alt || '';
    lightbox.classList.add('active');
    lightbox.setAttribute('aria-hidden', 'false');
    document.body.classList.add('lightbox-open');
}

function closeLightbox() {
    lightbox.classList.remove('active');
    lightbox.setAttribute('aria-hidden', 'true');
    document.body.classList.remove('lightbox-open');
    setTimeout(() => { lightboxImg.src = ''; }, 250);
}

function bindZoomables() {
    document.querySelectorAll('[data-zoomable]').forEach(wrapper => {
        wrapper.addEventListener('click', () => {
            const img = wrapper.querySelector('img');
            if (img) openLightbox(img.src, img.alt);
        });
    });
}

const handleHelp = document.getElementById('handleHelp');
const handleExampleImg = document.getElementById('handleExampleImg');
if (handleHelp && handleExampleImg) {
    // A imagem #handleExampleImg é baixada junto com a página (está no HTML).
    // No clique apenas reutilizamos essa versão já carregada, sem novo download.
    handleHelp.addEventListener('click', () => {
        openLightbox(handleExampleImg.src, handleExampleImg.alt);
    });
}

lightboxClose.addEventListener('click', closeLightbox);

lightbox.addEventListener('click', (e) => {
    if (e.target === lightbox) closeLightbox();
});

document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && lightbox.classList.contains('active')) {
        closeLightbox();
    }
});

// ===== FORM SUBMIT VIA FETCH =====
form.addEventListener('submit', async (e) => {
    e.preventDefault();

    clearError();
    resultsContainer.innerHTML = '';
    if (emptyState) emptyState.style.display = 'none';
    setLoading(true);

    try {
        const response = await fetch(form.action, {
            method: 'POST',
            headers: { 'X-Requested-With': 'XMLHttpRequest' },
            body: new FormData(form)
        });

        const data = await response.json();
        console.log(data);
        
        if (!response.ok || data.erro) {
            showError(data.erro || 'Ocorreu um erro ao analisar o canal.');
            return;
        }

        renderResults(data);
    } catch (err) {
        showError('Não foi possível concluir a análise. Tente novamente.');
    } finally {
        setLoading(false);
    }
});
