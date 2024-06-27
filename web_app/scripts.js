document.addEventListener('DOMContentLoaded', () => {
    const textLeft = document.getElementById('text-left');
    const textRight = document.getElementById('text-right');
    const browseButton = document.getElementById('browse-button');
    const fileInput = document.getElementById('file-input');
    const tidyButton = document.getElementById('tidy-button');
    const saveButton = document.getElementById('save-button');
    const exitButton = document.getElementById('exit-button');
    const outputMessage = document.getElementById('output-message');

    browseButton.addEventListener('click', () => {
        fileInput.click();
    });

    fileInput.addEventListener('change', (event) => {
        const file = event.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = (e) => {
                textLeft.value = e.target.result;
                outputMessage.value = `Loaded file: ${file.name}\n`;
            };
            reader.readAsText(file);
        }
    });

    tidyButton.addEventListener('click', () => {
        try {
            const content = textLeft.value;
            const simplifiedContent = simplifyBib(content);
            textRight.value = simplifiedContent;
            outputMessage.value += 'Tidied content.\n';
        } catch (e) {
            alert(`Failed to tidy content: ${e.message}`);
            outputMessage.value += `Failed to tidy content: ${e.message}\n`;
        }
    });

    saveButton.addEventListener('click', () => {
        const blob = new Blob([textRight.value], { type: 'text/plain;charset=utf-8' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'tidy.bib';
        a.click();
        URL.revokeObjectURL(url);
        outputMessage.value += 'Saved file.\n';
    });

    exitButton.addEventListener('click', () => {
        window.close();
    });

    function simplifyBib(content) {
        const prepositions = new Set(['of', 'the', 'and', 'in', 'on', 'for', 'with', 'a', 'an', 'by', 'at', 'to']);
        const specialWords = new Set(['IEEE', 'ACM', 'IEEE/ACM']);
        const bibDatabase = bibtexParse.toJSON(content);
        const fieldOrder = ['author', 'title', 'journal', 'year', 'volume', 'number', 'pages', 'month', 'note', 'abstract', 'keywords', 'source', 'doi'];
        let formattedBib = '';

        for (const entry of bibDatabase) {
            if (entry.entryTags.journal) {
                entry.entryTags.journal = capitalizeTitle(entry.entryTags.journal);
            }

            // Generate the ID
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
        const words = title.split(' ');
        const initials = words.slice(0, 5).map(word => {
            let initial = word[0];
            if (initial === '{' && word.length > 1) {
                initial = word[1];
            }
            return initial.toUpperCase();
        });
        return initials.join('');
    }

    function capitalizeTitle(title) {
        const prepositions = new Set(['of', 'the', 'and', 'in', 'on', 'for', 'with', 'a', 'an', 'by', 'at', 'to']);
        const specialWords = new Set(['IEEE', 'ACM', 'IEEE/ACM']);
        return title.split(' ').map(word => {
            if (word.startsWith('{') && word.endsWith('}')) return word;
            if (specialWords.has(word)) return word;
            if (prepositions.has(word.toLowerCase())) return word.toLowerCase();
            return word.charAt(0).toUpperCase() + word.slice(1).toLowerCase();
        }).join(' ');
    }
});
