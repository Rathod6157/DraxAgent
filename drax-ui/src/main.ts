import "./styles.css";

// Inline fallback mark avoids a build-time dependency on an optional logo asset.
const draxLogo =
  "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E%3Crect width='64' height='64' rx='18' fill='%23263f68'/%3E%3Cpath d='M32 10 39 25 54 32 39 39 32 54 25 39 10 32 25 25Z' fill='none' stroke='%239fc4ff' stroke-width='3' stroke-linejoin='round'/%3E%3Ccircle cx='32' cy='32' r='5' fill='%239fc4ff'/%3E%3C/svg%3E";

import { invoke } from "@tauri-apps/api/core";
import { listen } from "@tauri-apps/api/event";


type Sender =
  | "drax"
  | "user";


type DraxEvent = {

  type: string;

  text?: string;

  value?: boolean;

  message_type?: string;

  activity?: string;
  confidence?: number;
  application?: string;
  process?: string;
  window?: string;
  started_at?: number;
  context?: string;
  visual_context?: unknown;
  observed_at?: number;

  response?: DraxStructuredResponse;

  data?: Record<string, unknown>;

};


type DraxAction = {
  label?: string;
  command?: string;
  style?: string;
};


type DraxStructuredResponse = {
  type?: string;
  kind?: string;
  title?: string;
  icon?: string;
  data?: Record<string, unknown>;
  actions?: DraxAction[];
};


/* =========================================================
   DOM
   ========================================================= */

const conversation =
  document.querySelector<HTMLDivElement>(
    "#conversation"
  );


const form =
  document.querySelector<HTMLFormElement>(
    "#command-form"
  );


const input =
  document.querySelector<HTMLInputElement>(
    "#command-input"
  );


const sendButton =
  document.querySelector<HTMLButtonElement>(
    ".send-button"
  );


const activityCard =
  document.querySelector<HTMLElement>(
    ".activity-card"
  );


let activityTitle:
  HTMLDivElement | null =
  null;

let activityApplication:
  HTMLDivElement | null =
  null;

let activityWindow:
  HTMLDivElement | null =
  null;

let activityState:
  HTMLSpanElement | null =
  null;


/* =========================================================
   ACTIVITY CARD DOM NORMALIZATION
   Build ONE canonical layout regardless of what index.html
   currently contains. This prevents duplicate/stale labels.
   ========================================================= */

function normalizeActivityCard(): void {

  if (!activityCard) {
    return;
  }

  const content =
    activityCard.querySelector<HTMLDivElement>(
      ".activity-content"
    );

  if (!content) {
    return;
  }

  /* Remove legacy metrics from older Activity Card layouts.
     Drax no longer renders elapsed-time/confidence UI here. */
  activityCard
    .querySelectorAll(
      ".activity-metrics, .activity-time, .activity-duration, " +
      ".activity-confidence, .activity-confidence-row, " +
      ".activity-confidence-track, .activity-confidence-meter, " +
      ".activity-confidence-fill, .activity-right"
    )
    .forEach((element) => element.remove());


  /* -------------------------------------------------------
     ICON
     ------------------------------------------------------- */

  let icon =
    content.querySelector<HTMLDivElement>(
      ".activity-icon"
    );

  if (!icon) {

    icon =
      document.createElement("div");

    icon.className =
      "activity-icon";

    content.prepend(icon);
  }

  icon.textContent = "◈";
  icon.setAttribute("aria-hidden", "true");


  /* -------------------------------------------------------
     DETAILS
     ------------------------------------------------------- */

  let details =
    content.querySelector<HTMLDivElement>(
      ".activity-details"
    );

  if (!details) {

    details =
      document.createElement("div");

    details.className =
      "activity-details";

    content.appendChild(details);
  }


  activityTitle =
    details.querySelector<HTMLDivElement>(
      "#activity-title"
    );

  if (!activityTitle) {

    activityTitle =
      document.createElement("div");

    activityTitle.id =
      "activity-title";

    activityTitle.className =
      "activity-title";

    activityTitle.textContent =
      "Ready";

    details.prepend(activityTitle);
  }


  activityApplication =
    details.querySelector<HTMLDivElement>(
      "#activity-application"
    );

  if (!activityApplication) {

    activityApplication =
      document.createElement("div");

    activityApplication.id =
      "activity-application";

    activityApplication.className =
      "activity-application";

    activityApplication.textContent =
      "Waiting for your command";

    details.appendChild(
      activityApplication
    );
  }


  /* -------------------------------------------------------
     STATE
     ------------------------------------------------------- */

  activityState =
    details.querySelector<HTMLSpanElement>(
      "#activity-state"
    );

  if (!activityState) {

    activityState =
      document.createElement("span");

    activityState.id =
      "activity-state";

    activityState.className =
      "activity-state";

    activityState.textContent =
      "ANALYZED";

    activityApplication?.insertAdjacentElement(
      "afterend",
      activityState
    );
  }


  /* -------------------------------------------------------
     WINDOW
     ------------------------------------------------------- */

  activityWindow =
    details.querySelector<HTMLDivElement>(
      "#activity-window"
    );

  if (!activityWindow) {

    activityWindow =
      document.createElement("div");

    activityWindow.id =
      "activity-window";

    activityWindow.className =
      "activity-window";

    activityWindow.textContent =
      "Desktop";

    activityState?.insertAdjacentElement(
      "afterend",
      activityWindow
    );
  }



}


normalizeActivityCard();


const statusToast =
  document.querySelector<HTMLDivElement>(
    "#status-toast"
  );


const statusText =
  document.querySelector<HTMLSpanElement>(
    "#status-text"
  );


const statusIcon =
  document.querySelector<HTMLSpanElement>(
    "#status-icon"
  );


/* =========================================================
   STATE
   ========================================================= */

let busy = false;

let statusTimer:
  number | undefined;

/* =========================================================
   ACTIVITY CARD INTERACTION
   ========================================================= */

if (activityCard) {

  let spotlightFrame =
    0;

  activityCard.addEventListener(
    "pointermove",
    (event) => {

      if (spotlightFrame) {
        return;
      }

      spotlightFrame =
        window.requestAnimationFrame(() => {

          const rect =
            activityCard.getBoundingClientRect();

          activityCard.style.setProperty(
            "--mouse-x",
            `${event.clientX - rect.left}px`
          );

          activityCard.style.setProperty(
            "--mouse-y",
            `${event.clientY - rect.top}px`
          );

          activityCard.classList.add(
            "activity-pointer-active"
          );

          spotlightFrame = 0;
        });
    },
    { passive: true }
  );

  activityCard.addEventListener(
    "pointerleave",
    () => {
      activityCard.classList.remove(
        "activity-pointer-active"
      );
    }
  );
}


/* =========================================================
   SCROLL
   ========================================================= */

function scrollToBottom(): void {

  if (!conversation) {
    return;
  }

  requestAnimationFrame(
    () => {

      conversation.scrollTo({
        top:
          conversation.scrollHeight,

        behavior:
          "smooth",
      });

    }
  );
}


/* =========================================================
   STATUS ICONS / MICRO-INTERACTIONS
   ========================================================= */

function getStatusIcon(text: string): string {

  const value = text.toLowerCase();

  if (value.includes("looking") || value.includes("search")) {
    return `
      <svg viewBox="0 0 24 24" aria-hidden="true">
        <circle cx="11" cy="11" r="6.5"></circle>
        <path d="m16 16 4.2 4.2"></path>
      </svg>
    `;
  }

  if (value.includes("close") || value.includes("closing")) {
    return `
      <svg viewBox="0 0 24 24" aria-hidden="true">
        <path d="m7 7 10 10M17 7 7 17"></path>
      </svg>
    `;
  }

  if (value.includes("open") || value.includes("launch")) {
    return `
      <svg viewBox="0 0 24 24" aria-hidden="true">
        <path d="M12 3v12"></path>
        <path d="m7 10 5 5 5-5"></path>
        <path d="M5 20h14"></path>
      </svg>
    `;
  }

  if (value.includes("error") || value.includes("failed")) {
    return `
      <svg viewBox="0 0 24 24" aria-hidden="true">
        <path d="M12 3 2.8 20h18.4L12 3Z"></path>
        <path d="M12 9v5"></path>
        <path d="M12 17h.01"></path>
      </svg>
    `;
  }

  if (value.includes("thinking") || value.includes("processing")) {
    return `
      <svg viewBox="0 0 24 24" aria-hidden="true">
        <circle cx="6" cy="12" r="1.5"></circle>
        <circle cx="12" cy="12" r="1.5"></circle>
        <circle cx="18" cy="12" r="1.5"></circle>
      </svg>
    `;
  }

  if (value.includes("timer") || value.includes("countdown") || value.includes("remind")) {
    return `
      <svg viewBox="0 0 24 24" aria-hidden="true">
        <circle cx="12" cy="13" r="7"></circle>
        <path d="M9 3h6"></path>
        <path d="M12 13V9.5"></path>
        <path d="m12 13 2.5 1.5"></path>
      </svg>
    `;
  }

  if (value.includes("web") || value.includes("browser") || value.includes("chrome") || value.includes("edge")) {
    return `
      <svg viewBox="0 0 24 24" aria-hidden="true">
        <circle cx="12" cy="12" r="8.5"></circle>
        <circle cx="12" cy="12" r="3.2"></circle>
        <path d="M12 3.5v5.3"></path>
        <path d="M19.4 8.3 14.8 11"></path>
      </svg>
    `;
  }

  if (value.includes("application") || value.includes("app") || value.includes("program")) {
    return `
      <svg viewBox="0 0 24 24" aria-hidden="true">
        <rect x="4" y="4" width="16" height="16" rx="3"></rect>
        <path d="M8 8h3v3H8z"></path>
        <path d="M13 8h3"></path>
        <path d="M13 11h3"></path>
        <path d="M8 14h8"></path>
        <path d="M8 17h5"></path>
      </svg>
    `;
  }

  if (value.includes("ready") || value.includes("done") || value.includes("complete") || value.includes("success")) {
    return `
      <svg viewBox="0 0 24 24" aria-hidden="true">
        <circle cx="12" cy="12" r="8.5"></circle>
        <path d="m8 12.2 2.5 2.5 5.5-6"></path>
      </svg>
    `;
  }

  return `
    <svg viewBox="0 0 24 24" aria-hidden="true">
      <path d="m5 12 4.2 4.2L19 6.5"></path>
    </svg>
  `;
}


function cleanStatusText(text: string): string {
  // Status messages historically used emoji prefixes. Keep the
  // text, but move the visual indicator into our SVG icon.
  return text
    .replace(/^[\s\u{1F300}-\u{1FAFF}\u{2600}-\u{27BF}]+/u, "")
    .trim() || "Ready";
}


function pulseActivityCard(): void {

  if (!activityCard) {
    return;
  }

  activityCard.classList.remove("activity-changing");

  // Force a tiny reflow so consecutive window switches still retrigger
  // the transition instead of getting swallowed by the browser.
  void activityCard.offsetWidth;

  activityCard.classList.add("activity-changing");
}


function showStatus(
  text: string,
  duration = 1400,
): void {

  if (
    !statusToast ||
    !statusText
  ) {
    return;
  }


  if (
    statusTimer !== undefined
  ) {

    window.clearTimeout(
      statusTimer
    );
  }


  const cleanText =
    cleanStatusText(text);

  statusText.textContent =
    cleanText;

  if (statusIcon) {
    statusIcon.innerHTML =
      getStatusIcon(cleanText);
  }

  statusToast.classList.add(
    "visible"
  );


  statusTimer =
    window.setTimeout(
      () => {

        statusToast.classList.remove(
          "visible"
        );

      },
      duration
    );
}


/* =========================================================
   ACTIVITY
   ========================================================= */

function cleanWindowTitle(
  value: string,
): string {

  const text =
    value.trim();

  if (!text) {
    return "Desktop";
  }

  return text.length > 96
    ? `${text.slice(0, 93)}…`
    : text;
}




function updateActivity(
  title: string,
  application: string,
  windowTitle?: string,
  refined = true,
): void {

  pulseActivityCard();

  if (activityTitle) {
    activityTitle.textContent =
      title || "Unknown";
  }

  if (activityApplication) {
    activityApplication.textContent =
      application || "Unknown";
  }

  if (activityWindow) {
    activityWindow.textContent =
      cleanWindowTitle(
        windowTitle || ""
      );
  }

  if (activityState) {
    activityState.textContent =
      refined
        ? "ANALYZED"
        : "OBSERVING";

    activityState.classList.toggle(
      "is-observing",
      !refined
    );
  }
}

function updateActivityContext(
  application: string,
  windowTitle: string,
  observedAt?: number,
): void {
  // Reserved timestamp is accepted from the observer event; current UI uses live arrival time.
  void observedAt;

  const safeApplication =
    application ||
    "Unknown application";

  updateActivity(
    `Using ${safeApplication}`,
    safeApplication,
    windowTitle,
    false
  );
}


/* =========================================================
   MESSAGE CREATION
   ========================================================= */

/* =========================================================
   RICH Drax RESPONSE RENDERING
   ========================================================= */

function escapeHtml(
  value: string,
): string {

  return value
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}


function renderInlineMarkdown(
  value: string,
): string {

  let output =
    escapeHtml(value);

  output =
    output.replace(
      /`([^`]+)`/g,
      "<code>$1</code>"
    );

  output =
    output.replace(
      /\*\*([^*]+)\*\*/g,
      "<strong>$1</strong>"
    );

  output =
    output.replace(
      /__([^_]+)__/g,
      "<strong>$1</strong>"
    );

  output =
    output.replace(
      /(?<!\*)\*([^*]+)\*(?!\*)/g,
      "<em>$1</em>"
    );

  return output;
}


function renderRichMessage(
  text: string,
): HTMLDivElement {

  const container =
    document.createElement("div");

  container.className =
    "message-text rich-message";

  const lines =
    text
      .replace(/\r\n/g, "\n")
      .split("\n");

  let paragraph: string[] = [];
  let listItems: string[] = [];
  let inCode = false;
  let codeLanguage = "";
  let codeLines: string[] = [];

  const flushParagraph = (): void => {

    if (!paragraph.length) {
      return;
    }

    const block =
      document.createElement("p");

    block.innerHTML =
      paragraph
        .map(renderInlineMarkdown)
        .join("<br>");

    container.appendChild(block);

    paragraph = [];
  };


  const flushList = (): void => {

    if (!listItems.length) {
      return;
    }

    const list =
      document.createElement("ul");

    for (const item of listItems) {

      const li =
        document.createElement("li");

      li.innerHTML =
        renderInlineMarkdown(item);

      list.appendChild(li);
    }

    container.appendChild(list);

    listItems = [];
  };


  const flushCode = (): void => {

    const wrapper =
      document.createElement("div");

    wrapper.className =
      "rich-code-block";


    if (codeLanguage) {

      const language =
        document.createElement("div");

      language.className =
        "rich-code-language";

      language.textContent =
        codeLanguage;

      wrapper.appendChild(language);
    }


    const pre =
      document.createElement("pre");

    const code =
      document.createElement("code");

    code.textContent =
      codeLines.join("\n");

    pre.appendChild(code);
    wrapper.appendChild(pre);

    container.appendChild(wrapper);

    codeLines = [];
    codeLanguage = "";
  };


  for (const line of lines) {

    const fence =
      line.match(
        /^```([\w#+.-]*)\s*$/
      );

    if (fence) {

      if (inCode) {

        flushCode();
        inCode = false;

      } else {

        flushParagraph();
        flushList();

        inCode = true;
        codeLanguage =
          fence[1] || "";
      }

      continue;
    }


    if (inCode) {
      codeLines.push(line);
      continue;
    }


    if (!line.trim()) {
      flushParagraph();
      flushList();
      continue;
    }


    const heading =
      line.match(
        /^#{1,3}\s+(.+)$/
      );

    if (heading) {

      flushParagraph();
      flushList();

      const headingElement =
        document.createElement("h3");

      headingElement.innerHTML =
        renderInlineMarkdown(
          heading[1]
        );

      container.appendChild(
        headingElement
      );

      continue;
    }


    const bullet =
      line.match(
        /^\s*[-*]\s+(.+)$/
      );

    if (bullet) {

      flushParagraph();

      listItems.push(
        bullet[1]
      );

      continue;
    }


    const numbered =
      line.match(
        /^\s*\d+\.\s+(.+)$/
      );

    if (numbered) {

      flushParagraph();

      listItems.push(
        numbered[1]
      );

      continue;
    }


    flushList();

    paragraph.push(line);
  }


  if (inCode) {
    flushCode();
  }

  flushParagraph();
  flushList();


  if (!container.childNodes.length) {
    container.textContent = text;
  }


  return container;
}


function createDraxStructuredCard(
  response: DraxStructuredResponse,
): HTMLElement {

  const row =
    document.createElement("article");

  row.className =
    "message-row drax-row";


  const card =
    document.createElement("div");

  card.className =
    "message drax-message drax-structured-card";


  const header =
    document.createElement("div");

  header.className =
    "drax-card-header";


  const icon =
    document.createElement("span");

  icon.className =
    "drax-card-icon";

  icon.textContent =
    response.icon || "◈";


  const title =
    document.createElement("span");

  title.className =
    "drax-card-title";

  title.textContent =
    response.title || "Drax";


  header.appendChild(icon);
  header.appendChild(title);

  card.appendChild(header);


  const data =
    response.data || {};


  const content =
    document.createElement("div");

  content.className =
    "drax-card-content";


  const application =
    String(
      data.application || ""
    );

  const activity =
    String(
      data.activity || ""
    );

  const project =
    String(
      data.project || ""
    );

  const resourceName =
    String(
      data.resource_name || ""
    );

  const resourcePath =
    String(
      data.resource_path || ""
    );

  const windowTitle =
    String(
      data.window || ""
    );

  const confidence =
    Number(
      data.confidence || 0
    );


  if (application) {

    const app =
      document.createElement("div");

    app.className =
      "drax-card-app";

    app.textContent =
      application;

    content.appendChild(app);
  }


  if (activity) {

    const activityLine =
      document.createElement("div");

    activityLine.className =
      "drax-card-meta";

    activityLine.textContent =
      `● ${activity}`;

    content.appendChild(
      activityLine
    );
  }


  if (project) {

    const projectLine =
      document.createElement("div");

    projectLine.className =
      "drax-card-project";

    projectLine.textContent =
      project;

    content.appendChild(
      projectLine
    );
  }


  if (resourceName) {

    const file =
      document.createElement("div");

    file.className =
      "drax-file-card";


    const name =
      document.createElement("div");

    name.className =
      "drax-file-name";

    name.textContent =
      resourceName;


    const path =
      document.createElement("div");

    path.className =
      "drax-file-path";

    path.textContent =
      resourcePath ||
      "Path not resolved";


    file.appendChild(name);
    file.appendChild(path);

    content.appendChild(file);

  } else {

    const noFile =
      document.createElement("div");

    noFile.className =
      "drax-no-file";

    noFile.textContent =
      "No local file detected. "
      + "Your work context can still be an "
      + "application, activity, or window.";

    content.appendChild(noFile);
  }


  if (windowTitle) {

    const windowLine =
      document.createElement("div");

    windowLine.className =
      "drax-window-label";

    windowLine.textContent =
      `Window: ${windowTitle}`;

    content.appendChild(
      windowLine
    );
  }


  if (
    Number.isFinite(confidence)
    && confidence > 0
  ) {

    const confidenceLine =
      document.createElement("div");

    confidenceLine.className =
      "drax-confidence";

    confidenceLine.textContent =
      `${Math.round(confidence)}% context confidence`;

    content.appendChild(
      confidenceLine
    );
  }


  card.appendChild(content);


  const actions =
    response.actions || [];

  if (actions.length) {

    const actionBar =
      document.createElement("div");

    actionBar.className =
      "drax-card-actions";


    for (const action of actions) {

      if (!action.command) {
        continue;
      }

      const button =
        document.createElement("button");

      button.type =
        "button";

      button.className =
        action.style === "primary"
          ? "drax-action primary"
          : "drax-action";

      button.textContent =
        action.label || "Run";


      button.addEventListener(
        "click",
        () => {

          void sendCommand(
            action.command || ""
          );

        }
      );


      actionBar.appendChild(
        button
      );
    }


    card.appendChild(
      actionBar
    );
  }


  row.appendChild(card);

  return row;
}


function addStructuredResponse(
  response: DraxStructuredResponse,
): void {

  if (!conversation) {
    return;
  }

  removeThinking();

  conversation.appendChild(
    createDraxStructuredCard(
      response
    )
  );

  scrollToBottom();
}


function createMessage(
  sender: Sender,
  text: string,
): HTMLElement {

  const row =
    document.createElement(
      "article"
    );


  row.className =
    sender === "drax"
      ? "message-row drax-row"
      : "message-row user-row";


  const message =
    document.createElement(
      "div"
    );


  message.className =
    sender === "drax"
      ? "message drax-message"
      : "message user-message";


  /* -------------------------------------------------------
     HEADER
     ------------------------------------------------------- */

  const header =
    document.createElement(
      "div"
    );


  header.className =
    "message-header";


  if (
    sender === "drax"
  ) {

    const avatar =
      document.createElement(
        "div"
      );


    avatar.className =
      "message-avatar";


    const image =
      document.createElement(
        "img"
      );


    image.src =
      draxLogo;


    image.alt =
      "";


    avatar.appendChild(
      image
    );


    header.appendChild(
      avatar
    );
  }


  const senderLabel =
    document.createElement(
      "span"
    );


  senderLabel.className =
    "message-sender";


  senderLabel.textContent =
    sender === "drax"
      ? "Drax"
      : "You";


  const timeLabel =
    document.createElement(
      "span"
    );


  timeLabel.className =
    "message-time";


  timeLabel.textContent =
    "Now";


  header.appendChild(
    senderLabel
  );


  header.appendChild(
    timeLabel
  );


  /* -------------------------------------------------------
     TEXT
     ------------------------------------------------------- */

  let messageText: HTMLElement;

  if (sender === "drax") {

    messageText =
      renderRichMessage(text);

  } else {

    messageText =
      document.createElement("div");

    messageText.className =
      "message-text";

    messageText.textContent =
      text;
  }


  /* -------------------------------------------------------
     ASSEMBLE
     ------------------------------------------------------- */

  message.appendChild(
    header
  );


  message.appendChild(
    messageText
  );


  row.appendChild(
    message
  );


  return row;
}


/* =========================================================
   ADD MESSAGE
   ========================================================= */

function addMessage(
  sender: Sender,
  text: string,
): void {

  if (
    !conversation ||
    !text.trim()
  ) {
    return;
  }


  conversation.appendChild(
    createMessage(
      sender,
      text
    )
  );


  scrollToBottom();
}


/* =========================================================
   THINKING INDICATOR
   ========================================================= */

function showThinking(): void {

  if (!conversation) {
    return;
  }


  removeThinking();


  const row =
    document.createElement(
      "article"
    );


  row.className =
    "message-row drax-row";


  row.id =
    "thinking-row";


  const message =
    document.createElement(
      "div"
    );


  message.className =
    "message drax-message thinking-message";


  /* -------------------------------------------------------
     HEADER
     ------------------------------------------------------- */

  const header =
    document.createElement(
      "div"
    );


  header.className =
    "message-header";


  const avatar =
    document.createElement(
      "div"
    );


  avatar.className =
    "message-avatar";


  const image =
    document.createElement(
      "img"
    );


  image.src =
    draxLogo;


  image.alt =
    "";


  avatar.appendChild(
    image
  );


  header.appendChild(
    avatar
  );


  const senderLabel =
    document.createElement(
      "span"
    );


  senderLabel.className =
    "message-sender";


  senderLabel.textContent =
    "Drax";


  header.appendChild(
    senderLabel
  );


  /* -------------------------------------------------------
     THINKING CONTENT
     ------------------------------------------------------- */

  const thinkingContent =
    document.createElement(
      "div"
    );


  thinkingContent.className =
    "thinking-content";


  const thinkingText =
    document.createElement(
      "span"
    );


  thinkingText.textContent =
    "Drax is thinking";


  const dots =
    document.createElement(
      "span"
    );


  dots.className =
    "thinking-dots";


  for (
    let i = 0;
    i < 3;
    i += 1
  ) {

    const dot =
      document.createElement(
        "span"
      );


    dots.appendChild(
      dot
    );
  }


  thinkingContent.appendChild(
    thinkingText
  );


  thinkingContent.appendChild(
    dots
  );


  /* -------------------------------------------------------
     ASSEMBLE
     ------------------------------------------------------- */

  message.appendChild(
    header
  );


  message.appendChild(
    thinkingContent
  );


  row.appendChild(
    message
  );


  conversation.appendChild(
    row
  );


  scrollToBottom();
}


/* =========================================================
   REMOVE THINKING
   ========================================================= */

function removeThinking(): void {

  document
    .querySelector(
      "#thinking-row"
    )
    ?.remove();
}


/* =========================================================
   COMPOSER STATE
   ========================================================= */

function setBusy(
  value: boolean
): void {

  busy =
    value;


  if (input) {

    input.disabled =
      value;
  }


  if (sendButton) {

    sendButton.disabled =
      value;
  }
}


/* =========================================================
   COMMAND FINISHED
   ========================================================= */

function finishCommand(): void {

  removeThinking();


  setBusy(
    false
  );


  /*
   * The activity card represents the desktop, not the
   * conversation lifecycle. Never overwrite it with
   * "Ready" after a command finishes.
   */

  input?.focus();
}


/* =========================================================
   SEND
   ========================================================= */

async function sendCommand(
  command: string,
): Promise<void> {

  const text =
    command.trim();


  if (
    !text ||
    busy
  ) {
    return;
  }


  /* -------------------------------------------------------
     USER MESSAGE
     ------------------------------------------------------- */

  addMessage(
    "user",
    text
  );


  /* -------------------------------------------------------
     ACTIVITY
     ------------------------------------------------------- */




  showStatus(
    "Thinking...",
    1800
  );


  /* -------------------------------------------------------
     THINKING
     ------------------------------------------------------- */

  showThinking();


  /* -------------------------------------------------------
     INPUT
     ------------------------------------------------------- */

  if (input) {

    input.value =
      "";
  }


  setBusy(
    true
  );


  /* -------------------------------------------------------
     SEND TO PYTHON
     ------------------------------------------------------- */

  try {

    await invoke(
      "send_to_drax",
      {
        message: text
      }
    );

  } catch (error) {

    removeThinking();


    setBusy(
      false
    );





    showStatus(
      "Bridge error",
      1800
    );


    addMessage(
      "drax",
      `Something went wrong: ${String(error)}`
    );


    input?.focus();
  }
}


/* =========================================================
   FORM
   ========================================================= */

form?.addEventListener(
  "submit",
  (event) => {

    event.preventDefault();


    void sendCommand(
      input?.value ?? ""
    );
  }
);


/* =========================================================
   SUGGESTIONS
   ========================================================= */

document
  .querySelectorAll<HTMLButtonElement>(
    ".suggestion"
  )
  .forEach(
    (button) => {

      button.addEventListener(
        "click",
        () => {

          const command =
            button.dataset.command
              ?? "";


          void sendCommand(
            command
          );
        }
      );

    }
  );


/* =========================================================
   PYTHON EVENTS
   ========================================================= */

void listen<DraxEvent>(
  "drax://message",
  (event) => {

    const message =
      event.payload;


    switch (
      message.type
    ) {

      /* ---------------------------------------------------
         READY
         --------------------------------------------------- */

      case "ready":

        showStatus(
          "Drax is ready",
          1000
        );


        console.log(
          "Drax Python bridge ready."
        );

        break;


      /* ---------------------------------------------------
         THINKING
         --------------------------------------------------- */

      case "typing":

        if (
          message.value
        ) {

          showThinking();

        } else {

          removeThinking();
        }

        break;


      /* ---------------------------------------------------
         STATUS
         --------------------------------------------------- */

      case "status":

        if (
          message.text
        ) {

          showStatus(
            message.text,
            1800
          );
        }

        break;


      /* ---------------------------------------------------
         INSTANT DESKTOP OBSERVATION
         --------------------------------------------------- */

      case "activity_context":

        updateActivityContext(
          message.application ?? "Unknown application",
          message.window ?? "",
          message.observed_at
        );

        break;


      /* ---------------------------------------------------
         AI-REFINED DESKTOP ACTIVITY
         --------------------------------------------------- */

      case "activity_updated":

        updateActivity(
          message.activity ?? "Unknown",
          message.application ?? "Unknown application",
          message.window ?? "",
          true
        );

        break;


      /* ---------------------------------------------------
         OUTPUT
         --------------------------------------------------- */

      case "output": {

        const kind =
          message.message_type
            ?? "assistant";


        const text =
          message.text
            ?? "";


        if (!text.trim()) {
          break;
        }


        /* -----------------------------------------------
           ASSISTANT
           ----------------------------------------------- */

        if (
          kind === "assistant"
        ) {

          removeThinking();


          addMessage(
            "drax",
            text
          );




          showStatus(
            "Response ready",
            900
          );


          finishCommand();


          break;
        }


        /* -----------------------------------------------
           STATUS
           ----------------------------------------------- */

        if (
          kind === "status"
        ) {

          showStatus(
            text,
            1800
          );


          break;
        }


        /* -----------------------------------------------
           STATUS DONE
           ----------------------------------------------- */

        if (
          kind === "status_done"
        ) {

          showStatus(
            text,
            900
          );


          finishCommand();


          break;
        }


        /* -----------------------------------------------
           SUCCESS
           ----------------------------------------------- */

        if (
          kind === "success"
        ) {

          removeThinking();


          addMessage(
            "drax",
            `✅ ${text}`
          );





          showStatus(
            `✓ ${text}`,
            1200
          );


          finishCommand();


          break;
        }


        /* -----------------------------------------------
           ERROR
           ----------------------------------------------- */

        if (
          kind === "error"
        ) {

          removeThinking();


          addMessage(
            "drax",
            `❌ ${text}`
          );





          showStatus(
            "Something went wrong",
            1800
          );


          finishCommand();


          break;
        }


        /* -----------------------------------------------
           FALLBACK
           ----------------------------------------------- */

        addMessage(
          "drax",
          text
        );


        break;
      }


      /* ---------------------------------------------------
         STRUCTURED Drax RESPONSE
         --------------------------------------------------- */

      case "drax_response":

        removeThinking();

        if (
          message.response
          && typeof message.response === "object"
        ) {

          addStructuredResponse(
            message.response
          );

        } else if (message.text) {

          addMessage(
            "drax",
            message.text
          );
        }

        showStatus(
          "Response ready",
          900
        );

        finishCommand();

        break;


      /* ---------------------------------------------------
         DIRECT ASSISTANT MESSAGE
         --------------------------------------------------- */

      case "assistant_message":

        removeThinking();


        if (
          message.text
        ) {

          addMessage(
            "drax",
            message.text
          );
        }





        showStatus(
          "Response ready",
          900
        );


        finishCommand();


        break;


      /* ---------------------------------------------------
         COMMAND COMPLETE
         --------------------------------------------------- */

      case "command_complete":

        removeThinking();

        setBusy(
          false
        );

        input?.focus();

        break;

      case "status_done":

        showStatus(
          message.text
            ?? "Done",
          900
        );


        finishCommand();


        break;


      /* ---------------------------------------------------
         ERROR
         --------------------------------------------------- */

      case "error":

        removeThinking();


        addMessage(
          "drax",
          `❌ ${
            message.text
              ?? "Unknown error"
          }`
        );





        showStatus(
          "Something went wrong",
          1800
        );


        setBusy(
          false
        );


        input?.focus();


        break;


      /* ---------------------------------------------------
         UNKNOWN
         --------------------------------------------------- */

      default:

        console.log(
          "Unknown Drax event:",
          message
        );

        break;
    }
  }
);


/* =========================================================
   STARTUP
   ========================================================= */

if (input) {

  input.focus();
}


console.log(
  "Drax UI initialized."
);

/* =========================================================
   DRAX PRODUCT SHELL — local navigation and session list
   This layer does not change the Python/Tauri command contract.
   ========================================================= */
type LocalConversation = { id: string; title: string; updatedAt: number };
const SHELL_HISTORY_KEY = "drax.shell.conversations.v1";
const shellRoot = document.querySelector<HTMLElement>("#app");
const sectionView = document.querySelector<HTMLElement>("#section-view");
const chatView = document.querySelector<HTMLElement>("#chat-view");
const conversationList = document.querySelector<HTMLElement>("#conversation-list");
let activeConversationId = "session-default";
let shellHistory: LocalConversation[] = loadShellHistory();

function loadShellHistory(): LocalConversation[] {
  try {
    const raw = localStorage.getItem(SHELL_HISTORY_KEY);
    const parsed = raw ? JSON.parse(raw) : [];
    return Array.isArray(parsed) ? parsed.filter((item) =>
      item && typeof item.id === "string" && typeof item.title === "string"
    ) : [];
  } catch { return []; }
}
function saveShellHistory(): void {
  try { localStorage.setItem(SHELL_HISTORY_KEY, JSON.stringify(shellHistory.slice(0, 30))); }
  catch { /* Storage is optional; chat remains usable without it. */ }
}
function renderShellHistory(): void {
  if (!conversationList) return;
  conversationList.replaceChildren();
  if (!shellHistory.length) {
    const empty = document.createElement("div");
    empty.className = "conversation-item";
    empty.textContent = "No saved conversations yet";
    empty.style.opacity = ".55";
    empty.style.cursor = "default";
    conversationList.append(empty);
    return;
  }
  for (const item of shellHistory) {
    const button = document.createElement("button");
    button.type = "button";
    button.className = `conversation-item${item.id === activeConversationId ? " is-current" : ""}`;
    button.innerHTML = '<span class="conversation-glyph" aria-hidden="true">◌</span>';
    const title = document.createElement("span");
    title.className = "conversation-name";
    title.textContent = item.title;
    button.append(title);
    button.title = item.title;
    button.addEventListener("click", () => {
      // The MVP stores session labels locally; transcript restoration is a later persistence milestone.
      activeConversationId = item.id;
      renderShellHistory();
      showShellView("chat");
      showStatus("Conversation history restoration is planned for a future update.", 2200);
    });
    conversationList.append(button);
  }
}
function showShellView(view: string): void {
  document.querySelectorAll<HTMLButtonElement>("[data-view]").forEach((button) => {
    button.classList.toggle("is-active", button.dataset.view === view);
  });
  const isChat = view === "chat";
  if (chatView) chatView.hidden = !isChat;
  if (sectionView) {
    sectionView.hidden = isChat;
    if (!isChat) sectionView.innerHTML = getSectionMarkup(view);
  }
  shellRoot?.classList.remove("sidebar-open");
}
function getSectionMarkup(view: string): string {
  const pages: Record<string, { eyebrow: string; title: string; description: string; cards: Array<[string,string,string]>; note?: string }> = {
    projects: {
      eyebrow:"WORKSPACE", title:"Projects", description:"Keep related work, conversations, and context organized. Project linking is planned for the next MVP increment.",
      cards:[["▱","DraxAgent","The active product workspace. Connect a local folder when project management is wired into the agent."],["＋","Create a project","A dedicated project creation flow will arrive with persistent project storage."]]
    },
    library: {
      eyebrow:"YOUR KNOWLEDGE", title:"Library", description:"A home for files and useful references you choose to keep close to Drax.",
      cards:[["▥","Saved resources","Saved files and references will appear here once the library index is connected."],["⌕","Search your library","Search will use explicit indexed sources, not pretend to search files that have not been indexed."]]
    },
    activity: {
      eyebrow:"DESKTOP CONTEXT", title:"Activity", description:"See what Drax currently knows about the desktop. Screen observation and retention controls will be explicit and privacy-first.",
      cards:[["◉","Live desktop activity","The live activity card remains available in Chat. Detailed event history will be connected here."],["◈","Screen context","On-demand vision remains separate from continuous observation until privacy controls are implemented."]]
    },
    settings: {
      eyebrow:"PREFERENCES", title:"Settings", description:"Drax should make its behavior understandable and controllable. These controls are informational until connected to the backend.",
      cards:[]
    }
  };
  const page = pages[view] ?? pages.projects;
  const cards = page.cards.map(([icon,title,body]) => `<article class="section-card"><div class="section-card-icon" aria-hidden="true">${icon}</div><h3>${title}</h3><p>${body}</p></article>`).join("");
  const settings = view === "settings" ? `
    <div class="settings-row"><div><strong>Desktop activity</strong><small>Current activity card uses the existing observer integration.</small></div><span class="settings-status">Connected</span></div>
    <div class="settings-row"><div><strong>Screen observation</strong><small>Continuous screen capture is not enabled by this shell.</small></div><span class="settings-status">Not enabled</span></div>
    <div class="settings-row"><div><strong>Local conversation labels</strong><small>Store recent conversation names in this browser profile.</small></div><span class="settings-status">Local only</span></div>
    <div class="settings-row"><div><strong>Privacy controls</strong><small>Per-app and per-website exclusions are planned before background vision.</small></div><span class="settings-status">Planned</span></div>` : "";
  return `<div class="section-eyebrow">${page.eyebrow}</div><h1 class="section-title">${page.title}</h1><p class="section-description">${page.description}</p>${view === "settings" ? settings : `<div class="section-grid">${cards}</div>`}<div class="section-note">MVP transparency: this screen is a product-shell foundation. Features are not presented as connected until their backend behavior exists.</div>`;
}
function startNewShellConversation(): void {
  activeConversationId = `session-${Date.now()}`;
  const item: LocalConversation = { id: activeConversationId, title: "New conversation", updatedAt: Date.now() };
  shellHistory = [item, ...shellHistory.filter((entry) => entry.id !== item.id)].slice(0, 30);
  saveShellHistory();
  renderShellHistory();
  if (conversation) {
    conversation.replaceChildren();
    const article = document.createElement("article");
    article.className = "message-row drax-row";
    article.innerHTML = '<div class="message drax-message welcome-message"><div class="message-header"><div class="message-avatar"><img src="/src/assets/drax_logo.png" alt="" /></div><span class="message-sender">Drax</span><span class="message-time">Now</span></div><div class="message-text">New conversation. What are we working on?</div></div>';
    conversation.append(article);
  }
  showShellView("chat");
  input?.focus();
}
document.querySelectorAll<HTMLButtonElement>("[data-view]").forEach((button) => {
  button.addEventListener("click", () => showShellView(button.dataset.view ?? "chat"));
});
document.querySelector("#new-chat-button")?.addEventListener("click", startNewShellConversation);
document.querySelector("#sidebar-toggle")?.addEventListener("click", () => shellRoot?.classList.toggle("sidebar-open"));
const sidebarCollapseButton = document.querySelector<HTMLButtonElement>("#sidebar-collapse-button");
function setSidebarCollapsed(collapsed: boolean): void {
  shellRoot?.classList.toggle("sidebar-collapsed", collapsed);
  sidebarCollapseButton?.setAttribute("aria-pressed", String(collapsed));
  sidebarCollapseButton?.setAttribute("aria-label", collapsed ? "Expand sidebar" : "Collapse sidebar");
  sidebarCollapseButton?.setAttribute("title", collapsed ? "Expand sidebar" : "Collapse sidebar");
  try { sessionStorage.setItem("drax-sidebar-collapsed", String(collapsed)); } catch { /* storage may be unavailable */ }
}
try { setSidebarCollapsed(sessionStorage.getItem("drax-sidebar-collapsed") === "true"); } catch { setSidebarCollapsed(false); }
sidebarCollapseButton?.addEventListener("click", () => {
  setSidebarCollapsed(!shellRoot?.classList.contains("sidebar-collapsed"));
});
document.querySelector("#sidebar-scrim")?.addEventListener("click", () => shellRoot?.classList.remove("sidebar-open"));
document.querySelector("#clear-history-button")?.addEventListener("click", () => {
  shellHistory = [];
  activeConversationId = "session-default";
  saveShellHistory();
  renderShellHistory();
  showStatus("Recent conversation labels cleared.", 1800);
});
document.addEventListener("keydown", (event) => {
  if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "k") {
    event.preventDefault();
    startNewShellConversation();
  }
  if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "b") {
    event.preventDefault();
    setSidebarCollapsed(!shellRoot?.classList.contains("sidebar-collapsed"));
  }
});
renderShellHistory();
showShellView("chat");
