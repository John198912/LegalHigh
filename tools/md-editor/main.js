import { marked } from 'marked';
import Prism from 'prismjs';
import 'prismjs/themes/prism-tomorrow.css';

const input = document.getElementById('markdown-input');
const output = document.getElementById('preview-output');
const saveBtn = document.getElementById('save-btn');

// Configure marked with Prism highlighting
marked.setOptions({
  highlight: function(code, lang) {
    if (Prism.languages[lang]) {
      return Prism.highlight(code, Prism.languages[lang], lang);
    }
    return code;
  },
  breaks: true,
  gfm: true
});

// Load saved content
const savedContent = localStorage.getItem('legalhigh_draft');
if (savedContent) {
  input.value = savedContent;
  updatePreview();
} else {
  input.value = `# 法律分析文书草拟\n\n> 本编辑器专为 LegalHigh 项目设计。\n\n## 1. 案件概述\n在这里输入你的案件详情...\n\n\`\`\`javascript\nconsole.log("LegalHigh Intelligence Active");\n\`\`\``;
  updatePreview();
}

function updatePreview() {
  const content = input.value;
  output.innerHTML = marked.parse(content);
  localStorage.setItem('legalhigh_draft', content);
}

input.addEventListener('input', updatePreview);

saveBtn.addEventListener('click', () => {
  const blob = new Blob([input.value], { type: 'text/markdown' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'legal_draft.md';
  a.click();
  URL.revokeObjectURL(url);
});
