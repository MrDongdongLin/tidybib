document.addEventListener('DOMContentLoaded', () => {
    const textLeft = document.getElementById('text-left');
    const textRight = document.getElementById('text-right');
    const browseButton = document.getElementById('browse-button');
    const fileInput = document.getElementById('file-input');
    const tidyButton = document.getElementById('tidy-button');
    const saveButton = document.getElementById('save-button');
    const exitButton = document.getElementById('exit-button');
    const applyAbbreviation = document.getElementById('abbreviate-checkbox');
    const darkModeToggle = document.getElementById('dark-mode-toggle');
    const outputMessage = document.getElementById('output-message');

    let originalFileName = '';

    console.log('Loaded journal abbreviations:', journalAbbreviations);

    browseButton.addEventListener('click', () => {
        fileInput.click();
    });

    fileInput.addEventListener('change', (event) => {
        const file = event.target.files[0];
        if (file) {
            originalFileName = file.name.split('.')[0];
            const reader = new FileReader();
            reader.onload = (e) => {
                textLeft.value = e.target.result;
                applyHighlighting(); // 应用高亮显示
                outputMessage.value = `Loaded file: ${file.name}\n`;
            };
            reader.readAsText(file);
        }
    });

    tidyButton.addEventListener('click', () => {
        try {
            const content = textLeft.value;
            console.log("Original Content:", content);
            const simplifiedContent = simplifyBib(content, applyAbbreviation.checked);
            textRight.value = simplifiedContent;
            applyHighlighting(); // 应用高亮显示
            outputMessage.value += 'Tidied content.\n';
        } catch (e) {
            console.error(`Failed to tidy content: ${e.message}`);
            outputMessage.value += `Failed to tidy content: ${e.message}\n`;
        }
    });

    saveButton.addEventListener('click', () => {
        const blob = new Blob([textRight.value], { type: 'text/plain;charset=utf-8' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `tidy-${originalFileName}.bib`;
        a.click();
        URL.revokeObjectURL(url);
        outputMessage.value += 'Saved file.\n';
    });

    exitButton.addEventListener('click', () => {
        window.close();
    });

    darkModeToggle.addEventListener('click', () => {
        document.body.classList.toggle('dark-mode');
        darkModeToggle.textContent = document.body.classList.contains('dark-mode') ? 'Toggle Light Mode' : 'Toggle Dark Mode';
    });

    document.querySelectorAll('.copy-button').forEach(button => {
        button.addEventListener('click', () => {
            const targetId = button.getAttribute('data-target');
            const targetTextArea = document.getElementById(targetId);
            if (targetTextArea) {
                navigator.clipboard.writeText(targetTextArea.value).then(() => {
                    button.textContent = 'Copied!';
                    setTimeout(() => {
                        button.textContent = 'Copy';
                    }, 2000); // 2 seconds later, reset the button text
                }).catch(err => {
                    console.error('Failed to copy text: ', err);
                });
            }
        });
    });

    function simplifyBib(content, applyAbbreviation) {
        let bibDatabase;
        try {
            bibDatabase = bibtexParse.toJSON(content);
            console.log("Parsed BibTeX:", bibDatabase);
        } catch (error) {
            console.error("Error parsing BibTeX content:", error);
            throw new Error("Failed to parse BibTeX content");
        }
        
        const fieldOrder = ['author', 'title', 'journal', 'year', 'volume', 'number', 'pages', 'month', 'note', 'abstract', 'keywords', 'source', 'doi'];
        let formattedBib = '';

        for (const entry of bibDatabase) {
            const entryTags = {};
            for (const [key, value] of Object.entries(entry.entryTags || {})) {
                entryTags[key.toLowerCase()] = value;
            }
            entry.entryTags = entryTags;

            if (entry.entryTags.journal) {
                entry.entryTags.journal = capitalizeTitle(entry.entryTags.journal);
                if (applyAbbreviation) {
                    entry.entryTags.journal = abbreviateJournal(entry.entryTags.journal);
                }
            }

            let authorPart = '';
            if (entry.entryTags.author) {
                const authorNames = entry.entryTags.author.split(',');
                authorPart = authorNames[0].trim().split(' ')[0];
            }
            const yearPart = entry.entryTags.year ? entry.entryTags.year.trim() : 'noyear';
            const titlePart = entry.entryTags.title ? getTitlePart(entry.entryTags.title) : 'notitle';

            entry.citationKey = `${authorPart}:${yearPart}:${titlePart}`;

            formattedBib += `@${entry.entryType}{${entry.citationKey},\n`;
            fieldOrder.forEach(field => {
                if (entry.entryTags[field]) {
                    formattedBib += `  ${field.padEnd(12)} = {${entry.entryTags[field]}},\n`;
                }
            });
            formattedBib = formattedBib.trim().replace(/,$/, '') + '\n}\n\n';
        }
        return formattedBib.trim();
    }

    function getTitlePart(title) {
        if (!title) return 'notitle';
        const words = title.split(' ');
        const initials = words.slice(0, 5).map(word => {
            let initial = word[0];
            if (initial === '{' && word.length > 1) {
                initial = word[1];
            }
            return initial ? initial.toUpperCase() : '';
        });
        return initials.join('');
    }

    function capitalizeTitle(title) {
        if (!title) return '';
        const prepositions = new Set(['of', 'the', 'and', 'in', 'on', 'for', 'with', 'a', 'an', 'by', 'at', 'to']);
        const specialWords = new Set(['IEEE', 'ACM', 'IEEE/ACM']);
        const capitalizedTitle = title.split(' ').map(word => {
            if (word.startsWith('{') && word.endsWith('}')) return word;
            if (specialWords.has(word)) return word;
            if (prepositions.has(word.toLowerCase())) return word.toLowerCase();
            return word.charAt(0).toUpperCase() + word.slice(1).toLowerCase();
        }).join(' ');
        return capitalizedTitle;
    }

    function abbreviateJournal(journal) {
        const abbreviation = journalAbbreviations[journal];
        return abbreviation || journal;
    }

    function applyHighlighting() {
        const textAreas = document.querySelectorAll('.highlight-bibtex');
        textAreas.forEach(textArea => {
            const content = textArea.value;
            const highlightedContent = highlightBibtex(content);
            const highlightedDiv = textArea.nextElementSibling;
            if (highlightedDiv) {
                highlightedDiv.innerHTML = highlightedContent;
            }
        });
    }

    // 添加事件监听器以实时高亮
    textLeft.addEventListener('input', applyHighlighting);
    textRight.addEventListener('input', applyHighlighting);
});
