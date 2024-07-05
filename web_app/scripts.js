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

    // Set initial content
    const initialInputContent = `@inproceedings{ WOS:000766209400010,
Author = {Li, Yue and Abady, Lydia and Wang, Hongxia and Barni, Mauro},
Editor = {Zhao, X and Piva, A and ComesanaAlfaro, P},
Title = {A Feature-Map-Based Large-Payload DNN Watermarking Algorithm},
Booktitle = {DIGITAL FORENSICS AND WATERMARKING, IWDW 2021},
Series = {Lecture Notes in Computer Science},
Year = {2022},
Volume = {13180},
Pages = {135-148},
Note = {20th International Workshop on Digital-Forensics and Watermarking
   (IWDW), Beijing, PEOPLES R CHINA, NOV 20-22, 2021},
Organization = {Chinese Acad Sci, Inst Informat Engn, State Key Lab Informat Secur; New
   Jersey Institute of Technology; Springer},
DOI = {10.1007/978-3-030-95398-0\\_10},
ISSN = {0302-9743},
EISSN = {1611-3349},
ISBN = {978-3-030-95398-0; 978-3-030-95397-3},
Unique-ID = {WOS:000766209400010},
}`;
    const initialOutputContent = `@inproceedings{WOS:000766209400010,
  author =       {Li, Yue and Abady, Lydia and Wang, Hongxia and Barni, Mauro},
  title =        {A feature-map-based large-payload dnn watermarking algorithm},
  booktitle =    {Digital Forensics and Watermarking, Iwdw 2021},
  year =         {2022},
  editor =       {Zhao, X and Piva, A and ComesanaAlfaro, P},
  volume =       {13180},
  series =       {Lecture Notes in Computer Science},
  pages =        {135-148},
  doi =          {10.1007/978-3-030-95398-0\\_10},
}`;

    textLeft.value = initialInputContent;
    textRight.value = initialOutputContent;
    applyHighlighting(); // Apply initial highlighting

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
                applyHighlighting(); // Apply highlighting
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
            applyHighlighting(); // Apply highlighting
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

    // Add event listeners for real-time highlighting
    textLeft.addEventListener('input', applyHighlighting);
    textRight.addEventListener('input', applyHighlighting);
});
