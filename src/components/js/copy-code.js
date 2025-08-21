// copy-code.js
document.addEventListener('DOMContentLoaded', function() {
  // 复制图标SVG - 你可以替换成你选择的图标
  const copyIconSVG = `
   <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" stroke="currentColor" viewBox="0 0 256 256"><path d="M184,68H40a4,4,0,0,0-4,4V216a4,4,0,0,0,4,4H184a4,4,0,0,0,4-4V72A4,4,0,0,0,184,68Zm-4,144H44V76H180ZM220,40V184a4,4,0,0,1-8,0V44H72a4,4,0,0,1,0-8H216A4,4,0,0,1,220,40Z"></path></svg>
  `;

  // 复制成功图标SVG
  const checkIconSVG = `
  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" stroke="currentColor" viewBox="0 0 256 256">
    <path d="M229.66,77.66l-128,128a8,8,0,0,1-11.32,0l-56-56a8,8,0,0,1,11.32-11.32L96,188.69,218.34,66.34a8,8,0,0,1,11.32,11.32Z"></path>
  </svg>
  `;

  // 获取所有代码块
  const codeBlocks = Array.from(document.querySelectorAll("pre"));

  codeBlocks.forEach((codeBlock) => {
    // 创建包装器
    const wrapper = document.createElement("div");
    wrapper.style.position = "relative";

    // 创建复制按钮
    const copyButton = document.createElement("button");
    copyButton.className = "copy-code";
    copyButton.innerHTML = copyIconSVG;
    copyButton.setAttribute("aria-label", "复制代码");
    copyButton.setAttribute("title", "复制代码");

    // 将按钮添加到代码块
    codeBlock.appendChild(copyButton);
    
    // 用包装器包裹代码块
    codeBlock.parentNode.insertBefore(wrapper, codeBlock);
    wrapper.appendChild(codeBlock);

    // 添加点击事件
    copyButton.addEventListener("click", async () => {
      await copyCode(codeBlock, copyButton);
    });
  });

  // 复制代码函数
  async function copyCode(block, button) {
    const code = block.querySelector("code");
    const text = code.innerText;

    try {
      await navigator.clipboard.writeText(text);
      
      // 视觉反馈 - 改为对勾图标
      button.innerHTML = checkIconSVG;
      // button.style.color = "#22c55e"; // 绿色，你可以改为你的CSS变量
      button.classList.add('copy-success');

      // 可选：代码块边框闪烁效果
    //   block.classList.add('copy-success');
      
      setTimeout(() => {
        button.innerHTML = copyIconSVG;
        button.style.color = ""; // 恢复原色
        button.classList.remove('copy-success');
        block.classList.remove('copy-success');
      }, 300);
      
    } catch (err) {
      console.error('复制失败:', err);
      
      // 复制失败的视觉反馈
      button.style.color = "#ef4444"; // 红色
      setTimeout(() => {
        button.style.color = "";
      }, 1000);
    }
  }
});