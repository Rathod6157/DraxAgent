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

  source?: string;
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

const statusToast =
  document.querySelector<HTMLDivElement>(
    "#status-toast"
  );

const statusText =
  document.querySelector<HTMLSpanElement>(
    "#status-text"
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


/* =========================================================
   SCROLL
   ========================================================= */

function scrollToBottom(): void {

  if (!conversation) {
    return;
  }

  requestAnimationFrame(
    () => {

      /*
       * Immediate scrolling keeps message insertion stable.
       * Smooth scrolling during every DOM mutation was helping
       * create the old jump/disappear/reappear effect.
       */
      conversation.scrollTop =
        conversation.scrollHeight;

    }
  );
}


/* =========================================================
   STATUS TOAST
   ========================================================= */

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

  statusText.textContent =
    text;

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
   ACTIVITY CARD
   ========================================================= */

function formatElapsed(
  startedAt: number,
): string {

  /*
   * Python time.time() is seconds since Unix epoch.
   * Accept milliseconds too so this stays tolerant of future
   * protocol changes.
   */
  const startedMilliseconds =
    startedAt < 10_000_000_000
      ? startedAt * 1000
      : startedAt;

  const elapsedSeconds =
    Math.max(
      0,
      Math.floor(
        (
          Date.now()
          - startedMilliseconds
        ) / 1000
      )
    );

  if (
    elapsedSeconds < 5
  ) {
    return "Just now";
  }

  if (
    elapsedSeconds < 60
  ) {
    return `${elapsedSeconds}s`;
  }

  const minutes =
    Math.floor(
      elapsedSeconds / 60
    );

  const seconds =
    elapsedSeconds % 60;

  if (
    minutes < 60
  ) {

    return seconds === 0
      ? `${minutes}m`
      : `${minutes}m ${seconds}s`;
  }

  const hours =
    Math.floor(
      minutes / 60
    );

  const remainingMinutes =
    minutes % 60;

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
    formatElapsed(
      activityStartedAt
    );
}


function startActivityTimer(): void {

  if (
    activityTimer !== undefined
  ) {

    window.clearInterval(
      activityTimer
    );
  }

  activityTimer =
    window.setInterval(
      renderActivityTime,
      1000
    );
}


function updateActivity(
  activity: string,
  application: string,
  startedAt?: number,
): void {

  if (activityTitle) {

    activityTitle.textContent =
      activity || "Unknown";
  }

  if (activityApplication) {

    activityApplication.textContent =
      application || "Unknown";
  }

  if (
    startedAt !== undefined
    && Number.isFinite(startedAt)
  ) {

    activityStartedAt =
      startedAt;

    renderActivityTime();

    startActivityTimer();

    return;
  }

  if (activityTime) {

    activityTime.textContent =
      "Just now";
  }
}


/* =========================================================
   MESSAGE CREATION
   ========================================================= */

function createElement(
  tag: string,
  className: string,
): HTMLElement {

  const element =
    document.createElement(
      tag
    );

  element.className =
    className;

  return element;
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


  const header =
    createElement(
      "div",
      "message-header"
    );


  if (
    sender === "drax"
  ) {

    const avatar =
      createElement(
        "div",
        "message-avatar"
      );

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
    createElement(
      "span",
      "message-sender"
    );

  senderLabel.textContent =
    sender === "drax"
      ? "Drax"
      : "You";


  const timeLabel =
    createElement(
      "span",
      "message-time"
    );

  timeLabel.textContent =
    "Now";


  header.appendChild(
    senderLabel
  );

  header.appendChild(
    timeLabel
  );


  const messageText =
    createElement(
      "div",
      "message-text"
    );

  messageText.textContent =
    text;


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


function addMessage(
  sender: Sender,
  text: string,
): void {

  if (
    !conversation
    || !text.trim()
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

  thinkingText.className =
    "thinking-text";

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
  value: boolean,
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
   * The Activity Card represents the desktop, not the chat
   * command lifecycle. Never replace it with "Ready" here.
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
    !text
    || busy
  ) {
    return;
  }


  addMessage(
    "user",
    text
  );


  showStatus(
    "Thinking...",
    1800
  );

  showThinking();

  setBusy(
    true
  );


  if (input) {

    input.value =
      "";
  }


  try {

    await invoke(
      "send_to_drax",
      {
        message: text,
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

      case "ready":

        showStatus(
          "Drax is ready",
          1000
        );

        console.log(
          "Drax Python bridge ready."
        );

        break;


      case "typing":

        if (
          message.value
        ) {

          showThinking();

        } else {

          removeThinking();
        }

        break;


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
         LIVE DESKTOP ACTIVITY
         --------------------------------------------------- */

      case "activity_updated":

        updateActivity(
          message.activity
            ?? "Unknown",
          message.application
            ?? "Unknown",
          message.started_at
        );

        break;


      /* ---------------------------------------------------
         TERMINAL / SKILL OUTPUT
         --------------------------------------------------- */

      case "output": {

        const kind =
          message.message_type
            ?? "assistant";

        const text =
          message.text
            ?? "";

        if (
          !text.trim()
        ) {
          break;
        }


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


        if (
          kind === "status"
        ) {

          showStatus(
            text,
            1800
          );

          break;
        }


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


        addMessage(
          "drax",
          text
        );

        break;
      }


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


      case "status_done":

        showStatus(
          message.text
            ?? "Done",
          900
        );

        finishCommand();

        break;


      case "exit_requested":

        showStatus(
          "Goodbye",
          1000
        );

        finishCommand();

        break;


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

input?.focus();

console.log(
  "Drax UI initialized."
);
