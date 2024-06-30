function highlightBibtex(text) {
    const keywords = /@(?:article|book|booklet|conference|inbook|incollection|inproceedings|manual|mastersthesis|misc|phdthesis|proceedings|techreport|unpublished)\b/gi;
    const fields = /\b(author|title|journal|year|volume|number|pages|month|note|abstract|keywords|source|doi)\b/gi;
    const specialChars = /[\{\}]/g;
    const numbers = /\b\d{4}\b/g;

    // Preserve formatting by replacing newlines with <br> and spaces with &nbsp;
    const formattedText = text
        .replace(/\n/g, '<br>')
        .replace(/ /g, '&nbsp;')
        .replace(keywords, '<span class="bibtex-keyword">$&</span>')
        .replace(fields, '<span class="bibtex-field">$&</span>')
        .replace(specialChars, '<span class="bibtex-special-char">$&</span>')
        .replace(numbers, '<span class="bibtex-number">$&</span>');

    return `<pre><code>${formattedText}</code></pre>`;
}

function applyHighlighting() {
    const textAreas = document.querySelectorAll('.highlight-bibtex');
    textAreas.forEach(textArea => {
        const content = textArea.value;
        const highlightedContent = highlightBibtex(content);
        const highlightedDiv = document.createElement('div');
        highlightedDiv.className = 'highlighted-content';
        highlightedDiv.innerHTML = highlightedContent;
        textArea.style.display = 'none';
        textArea.parentNode.insertBefore(highlightedDiv, textArea.nextSibling);
    });
}

// Export functions if in module context
if (typeof module !== 'undefined' && typeof module.exports !== 'undefined') {
    module.exports = {
        highlightBibtex,
        applyHighlighting
    };
} else {
    window.highlightBibtex = highlightBibtex;
    window.applyHighlighting = applyHighlighting;
}
