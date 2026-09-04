import "./styles.css";

import draxLogo from "./assets/drax_logo.png";

type Sender = "drax" | "user";

const conversation = document.querySelector<HTMLDivElement>(
  "#conversation",
);

const form = document.querySelector<HTMLFormElement>(
  "#command-form",
);

const input = document.querySelector<HTMLInputElement>(
  "#command-input",
);

const activityTitle = document.querySelector<HTMLDivElement>(
  "#activity-title",
);

const activityApplication = document.querySelector<HTMLDivElement>(
  "#activity-application",
);

const activityTime = document.querySelector<HTMLDivElement>(
  "#activity-time",
);

const statusToast = document.querySelector<HTMLDivElement>(
  "#status-toast",
);

const statusText = document.querySelector<HTMLSpanElement>(
  "#status-text",
);


/* =========================================================
   HELPERS
   ========================================================= */

function scrollToBottom(): void {
  if (!conversation) {
    return;
  }

  requestAnimationFrame(() => {
    conversation.scrollTo({
      top: conversation.scrollHeight,
      behavior: "smooth",
    });
  });
}


function showStatus(
  message: string,
  duration = 1400,
): void {
  if (!statusToast || !statusText) {
    return;
  }

  statusText.textContent = message;

  statusToast.classList.add("visible");

  window.setTimeout(() => {
    statusToast.classList.remove("visible");
  }, duration);
}


function updateActivity(
  title: string,
  application: string,
): void {
  if (activityTitle) {
    activityTitle.textContent = title;
  }

  if (activityApplication) {
    activityApplication.textContent = application;
  }

  if (activityTime) {
    activityTime.textContent = "Just now";
  }
}


/* =========================================================
   MESSAGE BUILDING
   ========================================================= */

function createElement(
  tag: string,
  className: string,
): HTMLElement {
  const element =
    document.createElement(tag);

  element.className =
    className;

  return element;
}


function createMessage(
  sender: Sender,
  text: string,
): HTMLElement {
  const row =
    document.createElement("article");

  row.className =
    sender === "drax"
      ? "message-row drax-row"
      : "message-row user-row";


  const message =
    document.createElement("div");

  message.className =
    sender === "drax"
      ? "message drax-message"
      : "message user-message";


  /* -------------------------------------------------------
     HEADER
     ------------------------------------------------------- */

  const header =
    createElement(
      "div",
      "message-header",
    );


  if (sender === "drax") {

    const avatar =
      createElement(
        "div",
        "message-avatar",
      );

    const image =
      document.createElement("img");

    image.src =
      draxLogo;

    image.alt =
      "";

    avatar.appendChild(
      image,
    );

    header.appendChild(
      avatar,
    );
  }


  const senderLabel =
    createElement(
      "span",
      "message-sender",
    );

  senderLabel.textContent =
    sender === "drax"
      ? "Drax"
      : "You";


  const timeLabel =
    createElement(
      "span",
      "message-time",
    );

  timeLabel.textContent =
    "Now";


  header.appendChild(
    senderLabel,
  );

  header.appendChild(
    timeLabel,
  );


  /* -------------------------------------------------------
     MESSAGE TEXT
     ------------------------------------------------------- */

  const messageText =
    createElement(
      "div",
      "message-text",
    );

  /*
   * IMPORTANT:
   *
   * Use textContent instead of inserting the text into
   * an indented HTML template.
   *
   * This completely eliminates accidental leading spaces
   * and newlines from our source-code formatting.
   */
  messageText.textContent =
    text;


  /* -------------------------------------------------------
     ASSEMBLE
     ------------------------------------------------------- */

  message.appendChild(
    header,
  );

  message.appendChild(
    messageText,
  );

  row.appendChild(
    message,
  );

  return row;
}


function addMessage(
  sender: Sender,
  text: string,
): void {
  if (!conversation) {
    return;
  }

  conversation.appendChild(
    createMessage(
      sender,
      text,
    ),
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
    document.createElement("article");

  row.className =
    "message-row drax-row";

  row.id =
    "thinking-row";


  const message =
    document.createElement("div");

  message.className =
    "message drax-message thinking-message";


  /* Header */

  const header =
    document.createElement("div");

  header.className =
    "message-header";


  const avatar =
    document.createElement("div");

  avatar.className =
    "message-avatar";


  const image =
    document.createElement("img");

  image.src =
    draxLogo;

  image.alt =
    "";


  avatar.appendChild(
    image,
  );

  header.appendChild(
    avatar,
  );


  const senderLabel =
    document.createElement("span");

  senderLabel.className =
    "message-sender";

  senderLabel.textContent =
    "Drax";


  header.appendChild(
    senderLabel,
  );


  /* Thinking content */

  const thinkingContent =
    document.createElement("div");

  thinkingContent.className =
    "thinking-content";


  const thinkingText =
    document.createElement("span");

  thinkingText.textContent =
    "Drax is thinking";


  const dots =
    document.createElement("span");

  dots.className =
    "thinking-dots";


  for (let i = 0; i < 3; i += 1) {
    const dot =
      document.createElement("span");

    dots.appendChild(
      dot,
    );
  }


  thinkingContent.appendChild(
    thinkingText,
  );

  thinkingContent.appendChild(
    dots,
  );


  /* Assemble */

  message.appendChild(
    header,
  );

  message.appendChild(
    thinkingContent,
  );

  row.appendChild(
    message,
  );

  conversation.appendChild(
    row,
  );

  scrollToBottom();
}


function removeThinking(): void {
  document
    .querySelector("#thinking-row")
    ?.remove();
}


/* =========================================================
   DEMO RESPONSE
   ========================================================= */

/*
 * Frontend-only demo.
 *
 * Python is still disconnected.
 * We will replace this with the Tauri <-> Python bridge
 * later.
 */

function simulateResponse(
  command: string,
): void {
  showThinking();

  window.setTimeout(() => {

    removeThinking();

    const normalized =
      command
        .trim()
        .toLowerCase();


    let response =
      "I'm ready. My Python brain isn't connected to this new interface yet — that's our next phase.";


    if (
      normalized.includes("chrome")
    ) {

      response =
        "Chrome command received. The new UI will hand this to the existing Drax backend once we connect the bridge.";

    } else if (
      normalized.includes("hello") ||
      normalized === "hi" ||
      normalized === "hey"
    ) {

      response =
        "Heyyy 😎 I'm alive. The new Drax body is officially online.";

    } else if (
      normalized.includes("what can you do")
    ) {

      response =
        "Soon? Pretty much everything your existing Drax brain already knows how to do. We're just giving it a much better face.";
    }


    addMessage(
      "drax",
      response,
    );


    updateActivity(
      "Conversing",
      "Drax",
    );


    showStatus(
      "Response ready",
    );

  }, 900);
}


/* =========================================================
   SEND
   ========================================================= */

function sendCommand(
  command: string,
): void {

  const text =
    command.trim();


  if (!text) {
    return;
  }


  addMessage(
    "user",
    text,
  );


  updateActivity(
    "Processing",
    "Drax",
  );


  showStatus(
    "Thinking...",
    1000,
  );


  if (input) {
    input.value = "";
    input.focus();
  }


  simulateResponse(
    text,
  );
}


/* =========================================================
   FORM
   ========================================================= */

form?.addEventListener(
  "submit",
  (event) => {

    event.preventDefault();

    sendCommand(
      input?.value ?? "",
    );
  },
);


/* =========================================================
   SUGGESTIONS
   ========================================================= */

document
  .querySelectorAll<HTMLButtonElement>(
    ".suggestion",
  )
  .forEach((button) => {

    button.addEventListener(
      "click",
      () => {

        const command =
          button.dataset.command ?? "";

        sendCommand(
          command,
        );
      },
    );
  });


/* =========================================================
   STARTUP
   ========================================================= */

if (input) {
  input.focus();
}


console.log(
  "Drax UI initialized.",
);