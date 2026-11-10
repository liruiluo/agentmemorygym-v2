const environmentData = {
  shop: {
    title: "Shop",
    counter: "01 / 05",
    description: "Search, compare, and purchase across six shopping sessions while the approved product evidence has to survive five context replacements.",
    native: "search + buy",
    memory: "confirmed attributes",
    file: ".agent_memory/CONTINUATION.md",
    footer: "A purchase chain that outlives any single context window."
  },
  coding: {
    title: "Coding",
    counter: "02 / 05",
    description: "Reproduce a failure, inspect a repository, patch the right file, and verify the result after the task has outgrown the active context.",
    native: "shell + patch",
    memory: "tests, decisions",
    file: ".agent_memory/CONTINUATION.md",
    footer: "The agent writes the evidence trail it will need later."
  },
  autoresearch: {
    title: "AutoResearch",
    counter: "03 / 05",
    description: "Iterate on a machine-learning task by writing experiments, reading outputs, and keeping the record of what worked across the horizon.",
    native: "run + report",
    memory: "experiments, results",
    file: ".agent_memory/CONTINUATION.md",
    footer: "A durable lab notebook built from ordinary file operations."
  },
  general: {
    title: "General",
    counter: "04 / 05",
    description: "Carry a long office-style task across a tool surface, where the material gathered early has to be available much later.",
    native: "tools + documents",
    memory: "findings, sources",
    file: ".agent_memory/CONTINUATION.md",
    footer: "Ordinary documents as the medium for long-horizon state."
  },
  visual: {
    title: "Visual",
    counter: "05 / 05",
    description: "Build a site to a brief, inspect rendered previews, and keep the design findings after the images leave the active context.",
    native: "build + inspect",
    memory: "preview findings",
    file: ".agent_memory/CONTINUATION.md",
    footer: "What the agent saw stays readable after the pixels are gone."
  }
};

function initIcons() {
  if (window.lucide) window.lucide.createIcons();
}

function initEnvironmentTabs() {
  const tabs = [...document.querySelectorAll(".env-tab")];
  const next = document.querySelector("#env-next");
  const title = document.querySelector("#env-title");
  const counter = document.querySelector("#env-counter");
  const description = document.querySelector("#env-description");
  const native = document.querySelector("#env-native");
  const memory = document.querySelector("#env-memory");
  const file = document.querySelector("#env-file");
  const footer = document.querySelector("#env-footer-copy");
  let activeIndex = 0;

  function selectEnvironment(key) {
    const data = environmentData[key];
    activeIndex = tabs.findIndex((tab) => tab.dataset.env === key);
    tabs.forEach((tab) => {
      const selected = tab.dataset.env === key;
      tab.classList.toggle("is-active", selected);
      tab.setAttribute("aria-selected", String(selected));
    });
    title.textContent = data.title;
    counter.textContent = data.counter;
    description.textContent = data.description;
    native.textContent = data.native;
    memory.textContent = data.memory;
    file.textContent = data.file;
    footer.textContent = data.footer;
  }

  tabs.forEach((tab) => tab.addEventListener("click", () => selectEnvironment(tab.dataset.env)));
  next?.addEventListener("click", () => selectEnvironment(tabs[(activeIndex + 1) % tabs.length].dataset.env));
}

function initChart() {
  const buttons = [...document.querySelectorAll(".legend-button")];
  const valueMap = {
    camg: ["97.1%", "26.6%", "55.5%", "38.3%"],
    compact: ["97.5%", "19.5%", "50.8%", "24.2%"],
    base: ["11.6%", "10.9%", "36.7%", "10.2%"]
  };
  buttons.forEach((button) => button.addEventListener("click", () => {
    const series = button.dataset.series;
    buttons.forEach((item) => item.classList.toggle("is-active", item === button));
    document.querySelectorAll(".chart-row").forEach((row, index) => {
      row.querySelectorAll(".bar").forEach((bar) => bar.classList.toggle("is-hidden", !bar.classList.contains(`bar-${series}`)));
      row.querySelector(".bar-value").textContent = valueMap[series][index];
    });
  }));
}

function initReveal() {
  const items = document.querySelectorAll(".reveal");
  if (!("IntersectionObserver" in window)) {
    items.forEach((item) => item.classList.add("is-visible"));
    return;
  }
  const observer = new IntersectionObserver((entries, io) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add("is-visible");
        io.unobserve(entry.target);
      }
    });
  }, { threshold: 0.12, rootMargin: "0px 0px -34px" });
  items.forEach((item) => observer.observe(item));
}

function initCitation() {
  const button = document.querySelector("#copy-citation");
  const original = button?.querySelector("span")?.textContent || "Copy citation";
  const citation = "Luo, Lirui; Mao, Kelong; Xia, Heming; Li, Rongqing; Yang, Xinwei; Chen, Luyu; Wong, Kieran; Guo, Yudong; Wang, Xinrui; Zhu, Jiayin; Gu, Simiu; Xu, Sulong; Fang, Cong. Coding Agent Memory Post-Training II: Unlocking the Memory Potential of Pre-trained File Operations for Long-Horizon Tasks via On-Policy Distillation. 2026.";
  button?.addEventListener("click", async () => {
    try {
      await navigator.clipboard.writeText(citation);
      button.querySelector("span").textContent = "Citation copied";
      setTimeout(() => { button.querySelector("span").textContent = original; }, 1800);
    } catch {
      button.querySelector("span").textContent = "Select from paper PDF";
      setTimeout(() => { button.querySelector("span").textContent = original; }, 1800);
    }
  });
}

initEnvironmentTabs();
initChart();
initReveal();
initCitation();
initIcons();
