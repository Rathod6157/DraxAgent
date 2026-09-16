import "./styles.css";

import draxLogo from "./assets/drax_logo.png";

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


const activityTitle =
  document.querySelector<HTMLDivElement>(
    "#activity-title"
  );


const activityApplication =
  document.querySelector<HTMLDivElement>(
    "#activity-application"
  );


const activityTime =
  document.querySelector<HTMLDivElement>(
    "#activity-time"
  );


const activityWindow =
  document.querySelector<HTMLDivElement>(
    "#activity-window"
  );


const activityConfidence =
  document.querySelector<HTMLDivElement>(
    "#activity-confidence"
  );


const activityConfidenceFill =
  document.querySelector<HTMLDivElement>(
    "#activity-confidence-fill"
  );


const activityState =
  document.querySelector<HTMLSpanElement>(
    "#activity-state"
  );


const activityCard =
  document.querySelector<HTMLElement>(
    ".activity-card"
  );


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

let activityStartedAt:
  number | undefined;

let activityTimer:
  number | undefined;

let lastActivityApplication =
  "";


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

function formatElapsed(
  startedAt: number,
): string {

  const startedMilliseconds =
    startedAt < 10_000_000_000
      ? startedAt * 1000
      : startedAt;

  const elapsedSeconds =
    Math.max(
      0,
      Math.floor(
        (Date.now() - startedMilliseconds) / 1000
      )
    );

  if (elapsedSeconds < 5) {
    return "Just now";
  }

  if (elapsedSeconds < 60) {
    return `${elapsedSeconds}s`;
  }

  const minutes = Math.floor(elapsedSeconds / 60);

  if (minutes < 60) {
    const seconds = elapsedSeconds % 60;
    return seconds === 0
      ? `${minutes}m`
      : `${minutes}m ${seconds}s`;
  }

  const hours = Math.floor(minutes / 60);
  const remainingMinutes = minutes % 60;

  return remainingMinutes === 0
    ? `${hours}h`
    : `${hours}h ${remainingMinutes}m`;
}


function renderActivityTime(): void {

  if (
    !activityTime
    || activityStartedAt === undefined
  ) {
    return;
  }

  activityTime.textContent =
    formatElapsed(activityStartedAt);
}


function startActivityTimer(): void {

  if (activityTimer !== undefined) {
    window.clearInterval(activityTimer);
  }

  activityTimer =
    window.setInterval(
      renderActivityTime,
      1000
    );
}


function updateConfidence(
  confidence?: number,
): void {

  if (!activityConfidence || !activityConfidenceFill) {
    return;
  }

  if (
    confidence === undefined
    || !Number.isFinite(confidence)
  ) {
    activityConfidence.textContent = "—";
    activityConfidenceFill.style.width = "0%";
    return;
  }

  const value = Math.max(0, Math.min(100, Math.round(confidence)));

  activityConfidence.textContent = `${value}%`;
  activityConfidenceFill.style.width = `${value}%`;
}


function cleanWindowTitle(
  value: string,
): string {

  const text = value.trim();

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
  startedAt?: number,
  windowTitle?: string,
  confidence?: number,
  refined = true,
): void {

  pulseActivityCard();

  if (activityTitle) {
    activityTitle.textContent = title || "Unknown";
  }

  if (activityApplication) {
    activityApplication.textContent = application || "Unknown";
  }

  if (activityWindow) {
    activityWindow.textContent =
      cleanWindowTitle(windowTitle || "");
  }

  if (activityState) {
    activityState.textContent =
      refined ? "ANALYZED" : "OBSERVING";

    activityState.classList.toggle(
      "is-observing",
      !refined
    );
  }

  if (startedAt !== undefined && Number.isFinite(startedAt)) {
    activityStartedAt = startedAt;
    renderActivityTime();
    startActivityTimer();
  } else if (activityTime) {
    activityTime.textContent = "Just now";
  }

  updateConfidence(confidence);
}


function updateActivityContext(
  application: string,
  windowTitle: string,
  observedAt?: number,
): void {

  const safeApplication =
    application || "Unknown application";

  lastActivityApplication =
    safeApplication;

  const startedAt =
    observedAt
    ?? Date.now() / 1000;

  updateActivity(
    `Using ${safeApplication}`,
    safeApplication,
    startedAt,
    windowTitle,
    undefined,
    false
  );
}


/* =========================================================
   MESSAGE CREATION
   ========================================================= */

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

  const messageText =
    document.createElement(
      "div"
    );


  messageText.className =
    "message-text";


  messageText.textContent =
    text;


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

  updateActivity(
    "Processing",
    "Drax"
  );


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


    updateActivity(
      "Error",
      "Drax bridge"
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
          message.started_at,
          message.window ?? "",
          message.confidence,
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


          updateActivity(
            "Conversing",
            "Drax"
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


          updateActivity(
            "Completed",
            "Drax"
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


          updateActivity(
            "Error",
            "Drax"
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


        updateActivity(
          "Conversing",
          "Drax"
        );


        showStatus(
          "Response ready",
          900
        );


        finishCommand();


        break;


      /* ---------------------------------------------------
         COMMAND COMPLETE
         --------------------------------------------------- */

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


        updateActivity(
          "Error",
          "Drax bridge"
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

startActivityTimer();

if (input) {

  input.focus();
}


console.log(
  "Drax UI initialized."
);