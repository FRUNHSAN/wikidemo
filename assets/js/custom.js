/**
 * Wiki.js 自定义JavaScript
 * 在Wiki.js管理后台 → 主题 → 自定义JS中导入
 */

// ==========================================
// 工具函数
// ==========================================

/**
 * 显示通知消息
 */
function showNotification(message, type = 'info') {
  const notification = document.createElement('div');
  notification.className = `notification notification-${type}`;
  notification.textContent = message;
  notification.style.cssText = `
    position: fixed;
    top: 20px;
    right: 20px;
    padding: 15px 20px;
    background: ${type === 'success' ? '#10b981' : type === 'error' ? '#ef4444' : '#3b82f6'};
    color: white;
    border-radius: 8px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    z-index: 9999;
    animation: slideIn 0.3s ease-out;
  `;

  document.body.appendChild(notification);

  setTimeout(() => {
    notification.remove();
  }, 3000);
}

/**
 * 复制到剪贴板
 */
async function copyToClipboard(text) {
  try {
    await navigator.clipboard.writeText(text);
    showNotification('已复制到剪贴板', 'success');
  } catch (err) {
    console.error('复制失败:', err);
    showNotification('复制失败', 'error');
  }
}

/**
 * 获取URL参数
 */
function getUrlParameter(name) {
  const urlParams = new URLSearchParams(window.location.search);
  return urlParams.get(name);
}

// ==========================================
// 页面增强功能
// ==========================================

/**
 * 添加回到顶部按钮
 */
function addBackToTopButton() {
  const button = document.createElement('button');
  button.innerHTML = '↑';
  button.className = 'back-to-top';
  button.style.cssText = `
    position: fixed;
    bottom: 30px;
    right: 30px;
    width: 50px;
    height: 50px;
    border-radius: 50%;
    background: #2563eb;
    color: white;
    border: none;
    font-size: 24px;
    cursor: pointer;
    opacity: 0;
    transition: all 0.3s ease;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    z-index: 1000;
  `;

  button.addEventListener('click', () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  });

  document.body.appendChild(button);

  window.addEventListener('scroll', () => {
    if (window.scrollY > 300) {
      button.style.opacity = '1';
    } else {
      button.style.opacity = '0';
    }
  });
}

/**
 * 为代码块添加复制按钮
 */
function addCodeCopyButtons() {
  const codeBlocks = document.querySelectorAll('pre');

  codeBlocks.forEach((block) => {
    const button = document.createElement('button');
    button.className = 'copy-code-btn';
    button.textContent = '复制';
    button.style.cssText = `
      position: absolute;
      top: 10px;
      right: 10px;
      padding: 5px 10px;
      background: rgba(255, 255, 255, 0.9);
      border: 1px solid #e2e8f0;
      border-radius: 4px;
      cursor: pointer;
      font-size: 12px;
      opacity: 0;
      transition: opacity 0.2s;
    `;

    block.style.position = 'relative';

    button.addEventListener('mouseenter', () => {
      button.style.opacity = '1';
    });

    button.addEventListener('mouseleave', () => {
      button.style.opacity = '0';
    });

    button.addEventListener('click', async () => {
      const code = block.querySelector('code');
      if (code) {
        await copyToClipboard(code.textContent);
        button.textContent = '已复制!';
        setTimeout(() => {
          button.textContent = '复制';
        }, 2000);
      }
    });

    block.appendChild(button);

    block.addEventListener('mouseenter', () => {
      button.style.opacity = '1';
    });

    block.addEventListener('mouseleave', () => {
      button.style.opacity = '0';
    });
  });
}

/**
 * 添加阅读进度条
 */
function addReadingProgress() {
  const progressBar = document.createElement('div');
  progressBar.className = 'reading-progress';
  progressBar.style.cssText = `
    position: fixed;
    top: 0;
    left: 0;
    height: 3px;
    background: linear-gradient(to right, #2563eb, #3b82f6);
    width: 0%;
    z-index: 9999;
    transition: width 0.1s;
  `;

  document.body.appendChild(progressBar);

  window.addEventListener('scroll', () => {
    const windowHeight = window.innerHeight;
    const documentHeight = document.documentElement.scrollHeight - windowHeight;
    const scrolled = window.scrollY;
    const progress = (scrolled / documentHeight) * 100;
    progressBar.style.width = `${progress}%`;
  });
}

/**
 * 自动展开目录
 */
function autoExpandTOC() {
  const toc = document.querySelector('.toc');
  if (toc) {
    toc.classList.add('expanded');
  }
}

/**
 * 添加页面最后更新时间提示
 */
function addLastModifiedTip() {
  const lastModified = document.lastModified;
  if (lastModified) {
    const date = new Date(lastModified);
    const formatted = date.toLocaleString('zh-CN');

    const tip = document.createElement('div');
    tip.className = 'last-modified-tip';
    tip.textContent = `最后更新: ${formatted}`;
    tip.style.cssText = `
      position: fixed;
      bottom: 10px;
      left: 10px;
      padding: 5px 10px;
      background: rgba(0, 0, 0, 0.7);
      color: white;
      border-radius: 4px;
      font-size: 12px;
      z-index: 1000;
    `;

    document.body.appendChild(tip);
  }
}

// ==========================================
// 初始化
// ==========================================

document.addEventListener('DOMContentLoaded', () => {
  // 添加回到顶部按钮
  addBackToTopButton();

  // 为代码块添加复制按钮
  addCodeCopyButtons();

  // 添加阅读进度条
  addReadingProgress();

  // 自动展开目录
  autoExpandTOC();

  // 添加最后更新时间提示（可选）
  // addLastModifiedTip();

  console.log('Wiki.js 自定义脚本已加载');
});

// 添加CSS动画
const style = document.createElement('style');
style.textContent = `
  @keyframes slideIn {
    from {
      transform: translateX(400px);
      opacity: 0;
    }
    to {
      transform: translateX(0);
      opacity: 1;
    }
  }
`;
document.head.appendChild(style);
